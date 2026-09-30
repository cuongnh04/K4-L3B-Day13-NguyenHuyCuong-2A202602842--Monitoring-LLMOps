"""
Audit logging module with strict schema, tamper-evident hash chaining,
and retention lifecycle policy.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUDIT_LOG_PATH = Path(os.getenv("AUDIT_LOG_PATH", "data/audit.jsonl"))
DEFAULT_RETENTION_DAYS = int(os.getenv("AUDIT_RETENTION_DAYS", "30"))


def _compute_record_hash(prev_hash: str, payload_str: str) -> str:
    combined = f"{prev_hash}|{payload_str}".encode("utf-8")
    return hashlib.sha256(combined).hexdigest()[:16]


def get_last_audit_hash() -> str:
    if not AUDIT_LOG_PATH.exists():
        return "GENESIS_00000000"
    last_line = ""
    with AUDIT_LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                last_line = line.strip()
    if not last_line:
        return "GENESIS_00000000"
    try:
        record = json.loads(last_line)
        return record.get("record_hash", "GENESIS_00000000")
    except Exception:
        return "GENESIS_00000000"


def record_audit_event(
    *,
    actor: str,
    action: str,
    resource: str,
    correlation_id: str,
    status: str = "SUCCESS",
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    prev_hash = get_last_audit_hash()
    ts = datetime.now(timezone.utc).isoformat()

    record_core = {
        "ts": ts,
        "actor": actor,
        "action": action,
        "resource": resource,
        "correlation_id": correlation_id,
        "status": status,
        "details": details or {},
    }

    record_hash = _compute_record_hash(prev_hash, json.dumps(record_core, sort_keys=True))
    full_record = {
        **record_core,
        "prev_hash": prev_hash,
        "record_hash": record_hash,
    }

    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(full_record, ensure_ascii=False) + "\n")

    return full_record


def prune_expired_logs(retention_days: int = DEFAULT_RETENTION_DAYS) -> int:
    if not AUDIT_LOG_PATH.exists():
        return 0
    now_ts = time.time()
    cutoff_ts = now_ts - (retention_days * 86400)

    kept_lines = []
    pruned_count = 0
    with AUDIT_LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                rec_dt = datetime.fromisoformat(rec["ts"].replace("Z", "+00:00"))
                if rec_dt.timestamp() >= cutoff_ts:
                    kept_lines.append(line)
                else:
                    pruned_count += 1
            except Exception:
                kept_lines.append(line)

    if pruned_count > 0:
        AUDIT_LOG_PATH.write_text("\n".join(kept_lines) + "\n", encoding="utf-8")

    return pruned_count

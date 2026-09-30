"""
Demonstration script to query and verify integrity of the audit log.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.audit_log import AUDIT_LOG_PATH, _compute_record_hash, record_audit_event


def verify_integrity() -> bool:
    if not AUDIT_LOG_PATH.exists():
        print("Audit log does not exist yet.")
        return True

    expected_prev = "GENESIS_00000000"
    is_valid = True
    line_num = 0

    with AUDIT_LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line_num += 1
            rec = json.loads(line.strip())
            prev_hash = rec.get("prev_hash")
            rec_hash = rec.get("record_hash")

            if prev_hash != expected_prev:
                print(f"[!] Hash chain broken at line {line_num}: expected prev {expected_prev}, got {prev_hash}")
                is_valid = False

            core = {k: v for k, v in rec.items() if k not in ["prev_hash", "record_hash"]}
            computed = _compute_record_hash(prev_hash, json.dumps(core, sort_keys=True))
            if computed != rec_hash:
                print(f"[!] Tampering detected at line {line_num}: expected hash {computed}, got {rec_hash}")
                is_valid = False

            expected_prev = rec_hash

    if is_valid:
        print(f"[✓] Integrity check PASSED: All {line_num} audit records verified via SHA-256 chain.")
    return is_valid


def main():
    parser = argparse.ArgumentParser(description="Audit Log Query & Verification Tool")
    parser.add_argument("--action", help="Filter by action (e.g., INCIDENT_ENABLE, CHAT_REQUEST)")
    parser.add_argument("--actor", help="Filter by actor")
    parser.add_argument("--verify", action="store_true", help="Verify cryptographic hash chain integrity")
    parser.add_argument("--seed-samples", action="store_true", help="Add sample audit records for demo")
    args = parser.parse_args()

    if args.seed_samples:
        record_audit_event(
            actor="admin-sec-ops",
            action="INCIDENT_INJECT",
            resource="/incidents/rag_slow/enable",
            correlation_id="req-c6f40a12",
            details={"incident": "rag_slow", "reason": "challenge verification"},
        )
        record_audit_event(
            actor="user-student-2A202602842",
            action="PROMPT_ROLLBACK",
            resource="day13-chat",
            correlation_id="req-v2-candidate-01",
            details={"from_version": 2, "to_version": 1, "label": "production"},
        )
        print("Seeded sample audit events.")

    if args.verify:
        verify_integrity()
        return

    if not AUDIT_LOG_PATH.exists():
        print("No audit log found. Use --seed-samples to generate demo records.")
        return

    matched = []
    with AUDIT_LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line.strip())
            if args.action and rec.get("action") != args.action:
                continue
            if args.actor and rec.get("actor") != args.actor:
                continue
            matched.append(rec)

    print(f"--- Audit Log Query Results ({len(matched)} matching records) ---")
    for r in matched:
        print(f"[{r['ts']}] Actor: {r['actor']} | Action: {r['action']} | Resource: {r['resource']} | Hash: {r['record_hash']}")


if __name__ == "__main__":
    main()

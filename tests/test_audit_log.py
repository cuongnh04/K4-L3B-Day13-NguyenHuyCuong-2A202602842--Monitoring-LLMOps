from __future__ import annotations

import json
from pathlib import Path

from app import audit_log


def test_audit_log_hash_chain_and_pruning(tmp_path: Path, monkeypatch) -> None:
    test_log = tmp_path / "test_audit.jsonl"
    monkeypatch.setattr(audit_log, "AUDIT_LOG_PATH", test_log)

    e1 = audit_log.record_audit_event(
        actor="tester",
        action="LOGIN",
        resource="/auth",
        correlation_id="req-test-1",
    )
    e2 = audit_log.record_audit_event(
        actor="tester",
        action="EXECUTE",
        resource="/chat",
        correlation_id="req-test-2",
    )

    assert e1["prev_hash"] == "GENESIS_00000000"
    assert e2["prev_hash"] == e1["record_hash"]

    # Verify content in file
    lines = [json.loads(line) for line in test_log.read_text(encoding="utf-8").splitlines()]
    assert len(lines) == 2
    assert lines[0]["record_hash"] == e1["record_hash"]
    assert lines[1]["prev_hash"] == e1["record_hash"]

    # Test pruning policy with future cutoff
    pruned = audit_log.prune_expired_logs(retention_days=0)
    assert pruned == 2

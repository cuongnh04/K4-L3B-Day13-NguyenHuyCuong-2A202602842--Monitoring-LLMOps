#!/usr/bin/env python3
"""
Pre-commit / CI automated security scanner for Secrets and PII.
Scans code, config, logs, and evidence for leaked credentials, private keys, or raw PII.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# High-risk patterns
SECRET_PATTERNS = {
    "Langfuse Secret Key": re.compile(r"sk-lf-[a-zA-Z0-9_-]{20,}"),
    "Generic Private Key": re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
    "OpenAI / OpenRouter API Key": re.compile(r"sk-(?:or-v1-)?[a-zA-Z0-9_-]{32,}"),
    "Hardcoded Password": re.compile(r"(?i)(?:password|passwd|secret)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
}

PII_PATTERNS = {
    "Raw Email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "Raw VN Phone": re.compile(r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9}(?!\d)"),
    "Raw CCCD": re.compile(r"\b\d{12}\b"),
    "Raw Credit Card": re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"),
}

EXCLUDE_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", "tests", "data"}
EXCLUDE_FILES = {".env.example", "scan_secrets.py", "pii.py", "validate_logs.py"}


def scan_file(file_path: Path) -> list[str]:
    violations = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        return [f"Could not read {file_path}: {exc}"]

    # Secret check
    for name, pattern in SECRET_PATTERNS.items():
        if pattern.search(content):
            violations.append(f"CRITICAL: {name} found in {file_path.relative_to(REPO_ROOT)}")

    # PII check only for tracked code & config (excluding sample data and tests)
    if "submission" in file_path.parts and file_path.suffix in [".md", ".json"]:
        for name, pattern in PII_PATTERNS.items():
            if pattern.search(content):
                violations.append(f"WARNING: Potential {name} in {file_path.relative_to(REPO_ROOT)}")

    return violations


def main() -> int:
    print("=" * 60)
    print("Automated Security & PII Leak Scanner — K4-L3B Day 13")
    print("=" * 60)

    total_scanned = 0
    all_violations = []

    for path in REPO_ROOT.rglob("*"):
        if path.is_file():
            if any(part in EXCLUDE_DIRS for part in path.parts):
                continue
            if path.name in EXCLUDE_FILES:
                continue
            total_scanned += 1
            violations = scan_file(path)
            all_violations.extend(violations)

    print(f"Total files scanned: {total_scanned}")
    if all_violations:
        print("\nVIOLATIONS FOUND:")
        for v in all_violations:
            print(f"  [!] {v}")
        print("\nScan Result: FAILED")
        return 1

    print("\nScan Result: PASSED. Zero credentials or secret leaks detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

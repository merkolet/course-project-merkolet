#!/usr/bin/env python3
"""
Generate a human-friendly summary of SCA findings.

Input:  EVIDENCE/P09/sca_report.json (Grype JSON format)
Output: EVIDENCE/P09/sca_summary.md
"""

from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPORT_PATH = Path("EVIDENCE/P09/sca_report.json")
SUMMARY_PATH = Path("EVIDENCE/P09/sca_summary.md")
MAX_HIGHLIGHTS = 5


def load_report() -> Dict[str, Any]:
    if not REPORT_PATH.exists():
        raise FileNotFoundError(f"SCA report not found at {REPORT_PATH}")
    with REPORT_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def severity_key(value: str) -> str:
    return (value or "UNKNOWN").upper()


def build_highlights(matches: List[Dict[str, Any]]) -> List[str]:
    highlights: List[str] = []
    for match in matches:
        vuln = match.get("vulnerability", {})
        artifact = match.get("artifact", {})
        severity = severity_key(vuln.get("severity", "UNKNOWN"))
        if severity not in {"CRITICAL", "HIGH"}:
            continue
        cve = vuln.get("id", "UNKNOWN")
        package = artifact.get("name", "unknown")
        version = artifact.get("version", "unknown")
        fix = vuln.get("fix", {}).get("versions") or []
        fix_hint = f"→ update to {fix[0]}" if fix else "→ no fixed version yet"
        highlights.append(
            f"- **{severity}** {cve} in `{package}` ({version}) {fix_hint}"
        )
        if len(highlights) >= MAX_HIGHLIGHTS:
            break
    if not highlights:
        highlights.append("- No Critical/High issues detected 🎉")
    return highlights


def write_summary(report: Dict[str, Any]) -> None:
    matches = report.get("matches", [])
    counts = Counter()
    for match in matches:
        severity = severity_key(
            match.get("vulnerability", {}).get("severity", "UNKNOWN")
        )
        counts[severity] += 1

    total = sum(counts.values())
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
    highlights = build_highlights(matches)

    commit = os.getenv("GITHUB_SHA") or "unknown"
    lines = [
        "# SCA Summary (P09)",
        "",
        f"- Generated: {generated_at}",
        f"- Commit: `{commit}`",
        f"- Total findings: {total}",
        "",
        "## Severity distribution",
    ]

    if total == 0:
        lines.append("- No vulnerabilities detected.")
    else:
        for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "NEGLIGIBLE", "UNKNOWN"]:
            lines.append(f"- {level}: {counts.get(level, 0)}")

    lines.extend(
        [
            "",
            "## Highlights / Next steps",
            *highlights,
            "",
            "> Plan: Track fixes or waivers in `policy/waivers.yml` and reference DS1",
            "> when reporting upstream.",
        ]
    )

    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = load_report()
    write_summary(report)


if __name__ == "__main__":
    main()

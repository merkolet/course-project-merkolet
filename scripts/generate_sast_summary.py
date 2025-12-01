#!/usr/bin/env python3
"""
Generate summary for SAST (Semgrep SARIF + Gitleaks JSON).
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

SEM_GREP_PATH = Path("EVIDENCE/P10/semgrep.sarif")
GITLEAKS_PATH = Path("EVIDENCE/P10/gitleaks.json")
SUMMARY_PATH = Path("EVIDENCE/P10/sast_summary.md")


def load_json(path: Path) -> Dict[str, Any] | List[Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def semgrep_summary(data: Dict[str, Any]) -> Dict[str, Any]:
    runs = data.get("runs", [])
    findings = []
    for run in runs:
        results = run.get("results", [])
        for result in results:
            rule = result.get("ruleId")
            level = result.get("level", "note").upper()
            message = result.get("message", {}).get("text", "")
            findings.append({"rule": rule, "level": level, "message": message})
    counts = Counter(f["level"] for f in findings)
    return {"total": len(findings), "counts": counts, "findings": findings[:5]}


def gitleaks_summary(data: Any) -> Dict[str, Any]:
    if isinstance(data, dict):
        leaks = data.get("findings") or data.get("results") or []
    elif isinstance(data, list):
        leaks = data
    else:
        leaks = []
    findings = []
    for leak in leaks:
        rule = leak.get("rule")
        secret = leak.get("secret") or ""
        file = leak.get("file") or leak.get("filePath")
        findings.append({"rule": rule, "file": file, "secret": secret[:4] + "***"})
    return {"total": len(findings), "findings": findings[:5]}


def write_summary(
    semgrep_data: Dict[str, Any], gitleaks_data: Dict[str, Any | List[Any]]
) -> None:
    semgrep = (
        semgrep_summary(semgrep_data)
        if semgrep_data
        else {"total": 0, "counts": {}, "findings": []}
    )
    gitleaks = (
        gitleaks_summary(gitleaks_data)
        if gitleaks_data
        else {"total": 0, "findings": []}
    )

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
    lines = [
        "# Static Analysis Summary (P10)",
        "",
        f"- Generated: {timestamp}",
        "",
        "## Semgrep",
        f"- Findings: {semgrep['total']}",
    ]
    if semgrep["total"]:
        for level in ["ERROR", "WARNING", "NOTE"]:
            if semgrep["counts"].get(level):
                lines.append(f"  - {level}: {semgrep['counts'][level]}")
        lines.append("")
        lines.append("### Sample findings")
        for finding in semgrep["findings"]:
            lines.append(
                f"- `{finding['rule']}` ({finding['level']}): {finding['message']}"
            )
    else:
        lines.append("- No Semgrep findings 🎉")

    lines.extend(
        [
            "",
            "## Gitleaks",
            f"- Findings: {gitleaks['total']}",
        ]
    )
    if gitleaks["total"]:
        lines.append("### Sample findings")
        for leak in gitleaks["findings"]:
            lines.append(
                f"- `{leak['rule']}` in {leak['file']} (secret prefix {leak['secret']})"
            )
    else:
        lines.append("- No hardcoded secrets detected 🎉")

    lines.extend(
        [
            "",
            "## Next steps",
            "- Triage new HIGH/CRITICAL Semgrep findings within 2 business days.",
            (
                "- Gitleaks findings → rotate secrets or extend allowlist in "
                "`security/.gitleaks.toml` with justification."
            ),
        ]
    )

    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    semgrep_data = load_json(SEM_GREP_PATH)
    gitleaks_data = load_json(GITLEAKS_PATH)
    write_summary(semgrep_data, gitleaks_data)


if __name__ == "__main__":
    main()

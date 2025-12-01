# P10 Evidence

Workflow `Static Security Checks` (`.github/workflows/static-analysis.yml`) генерирует следующие артефакты:

- `semgrep.sarif` — результат SAST (Semgrep p/ci + кастомные правила `security/semgrep/rules.yml`).
- `gitleaks.json` — отчёт по секретам (Gitleaks с конфигом `security/.gitleaks.toml`).
- `sast_summary.md` — краткий обзор найденных проблем и план действий.

Файлы используются в DS-разделе и для дальнейшего триажа. Артефакты не коммитятся вручную — их создаёт workflow и выгружает через `actions/upload-artifact`.

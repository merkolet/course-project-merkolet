# SecDev Course Template

Стартовый шаблон для студенческого репозитория (HSE SecDev 2025).

## Быстрый старт
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
uvicorn app.main:app --reload
```

## Ритуал перед PR
```bash
  ruff --fix .
  black .
  isort .
  pytest -q
  pre-commit run --all-files
```

## Тесты
```bash
pytest -q
```

## CI
В репозитории настроен workflow **CI/CD Pipeline** (см. `.github/workflows/ci.yml`) — required check для `main`.
Там же выполняются тесты, линтеры, сборка Docker-образа и мок-деплой.

## Security Evidence (P09)
- Workflow **Security Evidence** (`.github/workflows/security.yml`) генерирует SBOM и SCA-отчёты.
- Все артефакты складываются в `EVIDENCE/P09/` и загружаются как GitHub Actions artifacts.
- Структура описана в `EVIDENCE/P09/README.md`, отчёты можно использовать в DS1/финальном отчёте.

### Артефакты
- `EVIDENCE/P09/sbom.json` — Syft SBOM, привязан к коммиту.
- `EVIDENCE/P09/sca_report.json` — Grype SCA отчёт.
- `EVIDENCE/P09/sca_summary.md` — агрегированная сводка (Critical/High + план).

### Политика и waivers
- Общая политика: `policy/waivers.yml` (шаблон + пример).
- Все исключения либо фиксируются в этом файле, либо закрываются обновлениями зависимостей.

## Static Analysis (P10)
- Workflow **Static Security Checks** (`.github/workflows/static-analysis.yml`) выполняет SAST (Semgrep) и сканирование секретов (Gitleaks).
- Артефакты: `EVIDENCE/P10/semgrep.sarif`, `EVIDENCE/P10/gitleaks.json`, `EVIDENCE/P10/sast_summary.md`.
- Структура описана в `EVIDENCE/P10/README.md`.

## DAST (P11)
- Workflow **DAST (ZAP Baseline)** (`.github/workflows/dast.yml`) выполняет динамическое сканирование безопасности.
- Приложение поднимается через `docker compose` (реальная конфигурация), затем запускается ZAP baseline scan.
- Артефакты: `EVIDENCE/P11/zap_baseline.json`, `EVIDENCE/P11/zap_baseline.html`.
- Структура описана в `EVIDENCE/P11/README.md`.

## Контейнеры
```bash
docker build -t secdev-app .
docker run --rm -p 8000:8000 secdev-app
# или
docker compose up --build
```

## Эндпойнты
- `GET /health` → `{"status": "ok"}`
- `POST /items?name=...` — демо-сущность
- `GET /items/{id}`

## Формат ошибок
Все ошибки — JSON-обёртка:
```json
{
  "error": {"code": "not_found", "message": "item not found"}
}
```

См. также: `SECURITY.md`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`.

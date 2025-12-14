# P11 Evidence (DAST)

Workflow **DAST (ZAP Baseline)** (`.github/workflows/dast.yml`) выполняет динамическое сканирование безопасности приложения.

## Артефакты

- `zap_baseline.json` — JSON-отчёт ZAP baseline scan
- `zap_baseline.html` — HTML-отчёт для удобного просмотра

## Процесс

1. Приложение поднимается через `docker compose` (реальная конфигурация с PostgreSQL)
2. Ожидание готовности через health check
3. ZAP baseline scan против `http://localhost:8000`
4. Генерация отчётов в JSON и HTML форматах
5. Загрузка артефактов в GitHub Actions

## Использование

Отчёты используются для:
- Выявления уязвимостей в runtime
- Валидации security headers
- Проверки на OWASP Top 10
- Дальнейшего триажа и фиксов

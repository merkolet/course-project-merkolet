# NFR BDD Scenarios

## Обзор
Данный документ содержит BDD (Behavior Driven Development) сценарии для приемки нефункциональных требований.

## NFR-001: Производительность API

### Сценарий 1: Нормальная нагрузка - время отклика
```gherkin
Feature: API Performance - Response Time
  As a system administrator
  I want to ensure API responds within acceptable time limits
  So that users have good experience

Scenario: API responds within performance thresholds under normal load
  Given the API is running and healthy
  And there are 100 concurrent users making requests
  When I send 1000 requests to the /wishes endpoint
  Then the 95th percentile response time should be ≤ 200ms
  And the 99th percentile response time should be ≤ 500ms
  And the average response time should be ≤ 100ms
  And the error rate should be < 1%
```

### Сценарий 2: Негативный - превышение лимитов
```gherkin
Scenario: API handles load beyond capacity limits
  Given the API is running and healthy
  And there are 1000 concurrent users making requests
  When I send 10000 requests to the /wishes endpoint
  Then the system should not crash
  And the error rate should be < 10%
  And failed requests should return appropriate HTTP status codes
  And the system should recover within 30 seconds after load reduction
```

## NFR-004: Безопасность данных

### Сценарий 1: Валидация входных данных
```gherkin
Feature: Data Security - Input Validation
  As a security administrator
  I want to ensure all input data is properly validated
  So that the system is protected from malicious input

Scenario: Valid input data is accepted
  Given the API is running and healthy
  When I send a POST request to /wishes with valid data:
    | title | link | price_estimate | notes |
    | "Valid Title" | "https://example.com" | 100.50 | "Valid notes" |
  Then the response should be 201 Created
  And the data should be stored correctly
  And the response should contain the created wish with valid ID
```

### Сценарий 2: Негативный - SQL Injection защита
```gherkin
Scenario: System is protected against SQL injection
  Given the API is running and healthy
  When I send a GET request to /wishes with malicious parameters:
    | price_lt | "'; DROP TABLE wishes; --" |
  Then the response should be 400 Bad Request or 422 Unprocessable Entity
  And the database should remain intact
  And no SQL commands should be executed
  And the attempt should be logged as a security event
```

## NFR-003: Доступность системы

### Сценарий 1: Health check availability
```gherkin
Feature: System Availability
  As a system administrator
  I want to ensure system is highly available
  So that users can access the service when needed

Scenario: Health check endpoint is always available
  Given the API is running
  When I send a GET request to /health
  Then the response should be 200 OK
  And the response time should be ≤ 100ms
  And the response should contain {"status": "ok"}
  And this should work 99.9% of the time over 30 days
```

### Сценарий 2: Негативный - отказ системы
```gherkin
Scenario: System recovery after failure
  Given the API is running and healthy
  When the system experiences a failure
  And the health check returns 500 Internal Server Error
  Then the system should recover automatically within 15 minutes
  And the health check should return 200 OK after recovery
  And no data should be lost during the failure
  And the recovery should be logged for audit purposes
```

## Технические детали реализации

### Инструменты для тестирования
- **Load Testing**: Artillery, Locust, k6
- **Security Testing**: OWASP ZAP, Burp Suite
- **Monitoring**: Prometheus, Grafana, ELK Stack
- **Validation Testing**: Pytest, Hypothesis (fuzzing)

### Метрики для мониторинга
- Response time percentiles (p50, p95, p99)
- Request rate (RPS)
- Error rate by status code
- Memory and CPU usage
- Database connection pool status
- Log volume and error frequency

### Критерии приемки
- Все сценарии должны проходить автоматически
- Негативные сценарии должны корректно обрабатывать ошибки
- Метрики должны соответствовать заданным порогам
- Логи должны содержать достаточно информации для диагностики

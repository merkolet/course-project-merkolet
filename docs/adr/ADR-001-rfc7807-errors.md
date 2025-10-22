# ADR-001: RFC 7807 Error Format Implementation

## Context
Текущая система обработки ошибок использует простой JSON формат с полями `error.code` и `error.message`. Нужен стандартизированный формат для отладки и мониторинга.

## Decision
Реализовать стандарт RFC 7807 "Problem Details for HTTP APIs" для всех ошибок API.

**Ключевые поля:**
- `type` - URI идентификатор типа проблемы
- `title` - краткое описание проблемы
- `status` - HTTP статус код
- `detail` - детальное описание проблемы
- `correlation_id` - уникальный идентификатор запроса
- `timestamp` - время возникновения ошибки в UTC

**Маскирование чувствительных данных:**
- Пароли, токены заменяются на `***`
- Email адреса маскируются как `u***@domain.com`

## Alternatives
1. **Оставить текущий формат** (`error.code`, `error.message`)
   - Простота реализации
   - Нестандартный формат, плохая трассируемость

2. **Использовать HTTP status codes без деталей**
   - Минимальный размер ответа
   - Недостаточно информации для отладки

3. **RFC 7807 с полной реализацией**
   - Стандартизированный формат
   - Улучшенная трассируемость
   - Увеличение размера ответов

## Implementation
```python
# app/schemas/error.py
class ProblemDetail(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    correlation_id: str
    timestamp: datetime
```

## Consequences
- Стандартизированный формат ошибок
- Улучшенная трассируемость через correlation_id
- Защита чувствительных данных
- Увеличение размера ответов с ошибками

## Links
- **NFR**: NFR-004 (Безопасность), NFR-006 (Логирование)
- **Threat Model**: F1, F7 (DFD), RISK-004
- **Tests**: `tests/test_rfc7807_errors.py`
- **Implementation**:
  - `app/core/exceptions.py` - RFC 7807 Problem Detail model
  - `app/middleware/correlation.py` - Correlation ID middleware
  - `app/main.py` - Integration with FastAPI

## Verification Criteria
- [ ] Все ошибки возвращают RFC 7807 Problem Detail JSON
- [ ] Correlation ID присутствует в каждом ответе с ошибкой
- [ ] Чувствительные данные маскируются в error details
- [ ] Content-Type: application/problem+json для всех ошибок

## Rollout Plan
1. **Phase 1**: Реализация базового RFC 7807 формата
2. **Phase 2**: Добавление correlation ID middleware
3. **Phase 3**: Внедрение маскирования чувствительных данных
4. **Phase 4**: Обновление всех error handlers
5. **Phase 5**: Тестирование и мониторинг в production

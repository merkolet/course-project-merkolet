# ADR-003: DateTime and Currency Normalization

## Context
Текущая система использует `datetime.now()` для временных меток и `float` для денежных значений. Это может привести к проблемам с часовыми поясами и ошибкам округления.

## Decision
Реализовать нормализацию дат и денежных значений с использованием UTC для всех временных меток и `Decimal` для денежных вычислений.

**Ключевые принципы:**
1. Все даты хранить в UTC
2. Использовать Decimal для денежных вычислений
3. Валидировать временные зоны при вводе
4. Поддержка различных валют (USD, EUR, RUB, GBP)

## Alternatives
1. **Оставить текущий подход** (`datetime.now()`, `float`)
   - Простота реализации
   - Проблемы с часовыми поясами и округлением

2. **Использовать только UTC без валидации**
   - Консистентность
   - Нет поддержки пользовательских временных зон

3. **Полная нормализация с валидацией**
   - Точность вычислений
   - Поддержка временных зон
   - Увеличение сложности

## Implementation
```python
# app/core/datetime_utils.py
class DateTimeNormalizer:
    @staticmethod
    def now_utc() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def to_utc(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

# app/core/currency_utils.py
class CurrencyNormalizer:
    @staticmethod
    def normalize_amount(amount: Union[float, str, Decimal], currency: str = 'USD') -> Decimal:
        decimal_amount = Decimal(str(amount))
        return decimal_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
```

## Consequences
- Точные денежные вычисления без ошибок округления
- Консистентные временные метки в UTC
- Увеличение сложности в обработке дат

## Links
- **NFR**: NFR-005 (Валидация), NFR-004 (Безопасность)
- **Threat Model**: F3-F4 (DFD), RISK-006
- **Tests**: `tests/test_datetime_currency_normalization.py`

## Verification Criteria
- [ ] Все даты сохраняются в UTC
- [ ] Денежные значения используют Decimal
- [ ] Валидация временных зон работает корректно
- [ ] Поддержка всех заявленных валют

## Rollout Plan
1. **Phase 1**: Создание DateTimeNormalizer и CurrencyNormalizer классов
2. **Phase 2**: Обновление Pydantic схем для использования новых типов
3. **Phase 3**: Миграция существующих данных в новые форматы
4. **Phase 4**: Обновление API endpoints для работы с нормализованными данными
5. **Phase 5**: Тестирование и валидация в production

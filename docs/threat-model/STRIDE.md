# STRIDE Threat Analysis

## Обзор
Данный документ содержит анализ угроз по методологии STRIDE для ключевых потоков данных Wishlist API. Каждая угроза связана с контрольными мерами и нефункциональными требованиями (NFR) из P03.

## Методология STRIDE

- **S**poofing - Подмена идентификации
- **T**ampering - Несанкционированное изменение данных
- **R**epudiation - Отказ от авторства действий
- **I**nformation Disclosure - Раскрытие конфиденциальной информации
- **D**enial of Service - Отказ в обслуживании
- **E**levation of Privilege - Повышение привилегий

## Анализ угроз по потокам

### F1: User → Load Balancer (HTTPS Request)

#### Угроза S-F1: Подмена пользователя (Spoofing)
**Описание**: Злоумышленник может выдать себя за легитимного пользователя, отправляя запросы от его имени.

**Контроль**:
- Реализация аутентификации (JWT tokens, OAuth 2.0)
- HTTPS для защиты учетных данных в транзите
- Rate limiting для предотвращения credential stuffing

**Связь с NFR**:
- **NFR-004**: Безопасность данных - требует защиты пользовательских данных
- **NFR-005**: Валидация входных данных - проверка токенов

**Проверка**:
- Unit тесты на валидацию токенов
- DAST тесты на authentication bypass (OWASP ZAP)

**Статус**: Частично - аутентификация в roadmap

---

### F1: User → Load Balancer (HTTPS Request)

#### Угроза D-F1: DDoS атака (Denial of Service)
**Описание**: Массовые запросы могут перегрузить систему и сделать ее недоступной для легитимных пользователей.

**Контроль**:
- Rate limiting на уровне Load Balancer
- WAF (Web Application Firewall)
- Auto-scaling для обработки всплесков нагрузки
- Connection limits

**Связь с NFR**:
- **NFR-002**: Пропускная способность ≥ 1000 RPS
- **NFR-003**: Доступность системы ≥ 99.9%
- **NFR-007**: Масштабируемость (≥ 3 реплики)

**Проверка**:
- Stress testing (Artillery, Locust)
- Monitoring alerts на аномальный трафик
- Load testing в CI/CD

**Статус**: Покрыто через NFR-002, NFR-007

---

### F3-F4: FastAPI ↔ Input Validator (Pydantic)

#### Угроза T-F3: Обход валидации (Tampering)
**Описание**: Злоумышленник может найти способ обойти Pydantic валидацию, отправив некорректные данные.

**Контроль**:
- Строгие Pydantic схемы с type hints
- Дополнительная валидация в бизнес-логике
- Input sanitization (защита от XSS, SQL injection)
- Fuzzing тестирование граничных случаев

**Связь с NFR**:
- **NFR-005**: Валидация входных данных - 100% через Pydantic, 0 bypass

**Проверка**:
- Unit тесты с edge cases (негативные сценарии)
- Fuzzing (hypothesis library)
- Code review на validation bypass
- Integration тесты с invalid payloads

**Статус**: Покрыто NFR-005, есть тесты

---

### F5-F6: FastAPI ↔ Database

#### Угроза I-F5: Раскрытие данных через SQL Injection (Information Disclosure)
**Описание**: SQL injection может позволить получить доступ к данным других пользователей.

**Контроль**:
- Использование ORM/query builder (SQLAlchemy в будущем)
- Prepared statements / parameterized queries
- Принцип минимальных привилегий для DB user
- Input validation до DB запроса

**Связь с NFR**:
- **NFR-004**: Безопасность - 0 критических уязвимостей
- **NFR-005**: Валидация входных данных

**Проверка**:
- SAST сканирование (SonarQube, Bandit)
- SQLMap тестирование
- Code review на raw queries

**Статус**: In-memory DB (пока не актуально), готовность к миграции

---

### F7: FastAPI → Logs Storage

#### Угроза R-F7: Отказ от авторства действий (Repudiation)
**Описание**: Пользователь может отрицать совершение действий из-за недостаточного логирования.

**Контроль**:
- Comprehensive audit logging (кто, что, когда)
- Timestamp с timezone
- Immutable log storage
- Log integrity (signing/hashing)

**Связь с NFR**:
- **NFR-006**: Логирование и мониторинг - 100% покрытие, retention ≥ 90 дней

**Проверка**:
- Audit log completeness review
- Log tampering tests
- Retention policy verification

**Статус**: Базовое логирование есть, требуется расширение

---

### F10: Administrator → FastAPI (Admin Access)

#### Угроза E-F10: Повышение привилегий (Elevation of Privilege)
**Описание**: Обычный пользователь может получить административный доступ.

**Контроль**:
- Strong authentication для admin (MFA)
- Отдельный admin endpoint или интерфейс
- IP whitelisting для admin доступа
- Audit всех admin действий

**Связь с NFR**:
- **NFR-004**: Безопасность данных
- **NFR-006**: Логирование admin действий

**Проверка**:
- Privilege escalation тестирование
- RBAC enforcement tests
- Admin action audit review

**Статус**: Admin функции в roadmap

---

## Сводная таблица покрытия

| Поток/Компонент | S | T | R | I | D | E | NFR Coverage |
|---|:-:|:-:|:-:|:-:|:-:|:-:|---|
| F1 (User→LB) | X | - | - | - | X | - | NFR-002,003,004,005,007 |
| F3-F4 (Validation) | - | X | - | - | - | - | NFR-005 |
| F5-F6 (DB) | - | - | - | X | - | - | NFR-004,005 |
| F7 (Logs) | - | - | X | - | - | - | NFR-006 |
| F10 (Admin) | - | - | - | - | - | X | NFR-004,006 |

## Приоритеты внедрения

### High Priority
1. **Аутентификация/Авторизация** (S-F1, E-F10) → NFR-004
2. **Rate Limiting** (D-F1) → NFR-002, NFR-003
3. **Расширенный аудит** (R-F7) → NFR-006

### Medium Priority
4. **Fuzzing для валидации** (T-F3) → NFR-005
5. **ORM для защиты от SQL Injection** (I-F5) → NFR-004, NFR-005

## Метрики успеха

- **0 критических уязвимостей** в DAST/SAST сканировании (NFR-004)
- **100% покрытие валидации** через Pydantic (NFR-005)
- **Audit log coverage ≥ 95%** критических операций (NFR-006)
- **Успешный penetration test** без High findings

# ============================================================================
# Build stage - для установки зависимостей и тестирования
# ============================================================================
FROM python:3.11-slim AS build

# Установка build зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Копируем только файлы зависимостей для лучшего кэширования
COPY requirements.txt requirements-dev.txt ./

# Устанавливаем зависимости в виртуальное окружение
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements-dev.txt

COPY . .

# Запускаем тесты
RUN /opt/venv/bin/pytest tests/ -q

# ============================================================================
# Runtime stage - минимальный образ для запуска приложения
# ============================================================================
FROM python:3.11-slim AS runtime

# Создаем non-root пользователя
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1000 -m -s /bin/bash appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Копируем только виртуальное окружение из build stage
COPY --from=build /opt/venv /opt/venv

# Копируем код приложения (без тестов для runtime)
COPY --chown=appuser:appuser app/ /app/app/
COPY --chown=appuser:appuser pyproject.toml /app/

WORKDIR /app

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app"

# Переключаемся на non-root пользователя
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

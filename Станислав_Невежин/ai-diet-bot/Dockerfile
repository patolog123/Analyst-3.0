# Используем официальный Python образ с версией 3.11 для Amvera
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем системные зависимости для сборки Python пакетов
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Python зависимости для Amvera
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения
COPY . .

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Открываем порт для веб-сервера
EXPOSE 8080

# Переменные окружения по умолчанию для Amvera
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    ENVIRONMENT=production \
    PORT=8080 \
    PYTHONDONTWRITEBYTECODE=1 \
    BOT_TOKEN=${BOT_TOKEN:-8487301809:AAElsUyaMmEz2NUWM_jpk2r1AUbUKoSgeyE} \
    DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY:-sk-386c00f1f374421783d3225d40fdb08b} \
    DEEPSEEK_MODEL=deepseek-chat \
    DEEPSEEK_BASE_URL=https://api.deepseek.com \
    DEEPSEEK_TEMPERATURE=0.7 \
    DEEPSEEK_MAX_TOKENS=4000 \
    DEBUG=false \
    LOG_LEVEL=INFO \
    PORT=8080 \
    HOST=0.0.0.0 \
    API_BASE_URL=https://ai-diet-bot-snevezhin.amvera.io \
    CORS_ORIGINS=https://ai-diet-bot-snevezhin.amvera.io,http://0.0.0.0:8080 \
    CORS_ALLOW_CREDENTIALS=true \
    CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS \
    CORS_ALLOW_HEADERS=Content-Type,Authorization,X-Requested-With

# Команда запуска приложения
CMD ["python", "main.py"]
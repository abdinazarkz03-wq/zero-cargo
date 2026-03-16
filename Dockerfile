# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем только нужные файлы
COPY requirements.txt .
COPY bot.py .
COPY admin.py .
COPY config.py .
COPY database.py .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Переменные окружения через Railway или .env
ENV PYTHONUNBUFFERED=1

# Команда запуска бота
CMD ["python", "bot.py"]

# Используем легкий образ Python
FROM python:3.11-slim

# Рабочая директория
WORKDIR /app

# Копируем все файлы проекта внутрь контейнера
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Команда запуска бота
CMD ["python", "bot.py"]

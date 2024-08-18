# Используем официальный образ Python 3.11
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Копируем entrypoint скрипт и делаем его исполняемым
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Указываем порт, который будет использовать приложение
EXPOSE 8000

# Запускаем entrypoint скрипт
ENTRYPOINT ["./entrypoint.sh"]
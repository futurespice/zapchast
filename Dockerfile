# Используем официальный образ Python 3.11
FROM python:3.11

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y postgresql-client
# Копируем остальные файлы проекта
COPY . .

# Копируем entrypoint скрипт и делаем его исполняемым
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Указываем порт, который будет использовать приложение
EXPOSE 8000

# Запускаем entrypoint скрипт
ENTRYPOINT ["./entrypoint.sh"]
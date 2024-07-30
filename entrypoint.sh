#!/bin/sh

set -e

# Ждем, пока база данных будет готова
until PGPASSWORD=$SQL_PASSWORD psql -h "db" -U "$SQL_USER" -d "$SQL_DATABASE" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

# Применяем миграции
python manage.py migrate

# Собираем статические файлы
python manage.py collectstatic --noinput

# Запускаем сервер
exec "$@"
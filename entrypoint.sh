#!/bin/bash

# Применяем миграции
echo "Applying database migrations..."
python manage.py migrate

# Сборка статики
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Запускаем сервер
echo "Starting server..."
exec "$@"

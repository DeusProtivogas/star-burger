# Используем минималистичный базовый образ Python
FROM python:3.9-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Переменные окружения для оптимизации работы Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Создаём рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt /app/

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs=16.16.0-1nodesource1 \
    && apt-mark hold nodejs

# Копируем весь проект в контейнер
COPY . /app/

# Копируем entrypoint.sh и делаем его исполняемым
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Установите зависимости проекта
COPY package.json package-lock.json /app/
RUN npm install

# Соберите фронтенд
COPY bundles-src /app/bundles-src
RUN npm run build


# Собираем статические файлы
RUN python manage.py collectstatic --noinput

# Устанавливаем entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Указываем команду для запуска приложения
CMD ["gunicorn", "star_burger.wsgi:application", "--bind", "0.0.0.0:8000"]

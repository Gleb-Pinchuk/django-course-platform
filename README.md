# Django Course Platform

Django REST API для платформы онлайн-курсов с интеграцией платежей Stripe.

##  Функционал

- REST API для курсов и подписок
- Интеграция с Stripe для платежей
- Админ-панель Django
- Фоновые задачи с Celery + Redis
- Автоматический деплой через GitHub Actions

## 🛠️ Установка на сервере
### 1. Подготовка сервера

```bash
# Обновление пакетов
sudo apt update && sudo apt upgrade -y

# Установка зависимостей
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib redis-server nginx git
```

### 2. Настройка PostgreSQL

# Создать базу и пользователя
sudo -u postgres psql

# В PostgreSQL:
CREATE DATABASE drf_db;
CREATE USER drf_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE drf_db TO drf_user;
\c drf_db
GRANT ALL ON SCHEMA public TO drf_user;
\q

### 3. Клонирование репозитория

```bash
git clone https://github.com/Gleb-Pinchuk/django-course-platform.git
cd django-course-platform
```

### 4. Создание виртуального окружения

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

### 5. Настройка переменных окружения

cp .env.example .env
nano .env 

#### Примени миграции

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

### 6. Запуск через Gunicorn + Nginx

См. конфигурацию в папке nginx/ и systemd/.
CI/CD
Проект использует GitHub Actions для автоматического тестирования и деплоя.
Настройка Secrets на GitHub:
SSH_PRIVATE_KEY — приватный SSH ключ для доступа к серверу
SERVER_HOST — IP-адрес сервера
SERVER_USER — пользователь на сервере (ubuntu)
SECRET_KEY — секретный ключ Django
Workflow запускается автоматически:
При каждом push в ветку main или develop
Сначала запускаются тесты
После успешных тестов — деплой на сервер

# Настройка Secrets на GitHub:

SSH_PRIVATE_KEY   Содержимое приватного SSH ключа (.pem файл)
SERVER_HOST   IP-адрес сервера (например, 83.166.236.188)
SERVER_USER   Пользователь на сервере (ubuntu)
SECRET_KEY    Django SECRET_KEY из файла .env

## Тестирование

python manage.py test


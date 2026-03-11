# Django Course Platform
##  Функционал

- REST API для курсов и подписок
- Интеграция с Stripe для платежей
- Админ-панель Django
- Фоновые задачи с Celery + Redis
- Автоматический деплой через GitHub Actions

## 🛠️ Установка на сервере

### 1. Клонирование репозитория

```bash
git clone https://github.com/Gleb-Pinchuk/django-course-platform.git
cd django-course-platform
```

### 2. Создание виртуального окружения

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

### 3. Настройка переменных окружения

cp .env.example .env
nano .env 

### 4. Настройка базы данных

#### Создай базу данных PostgreSQL
sudo -u postgres psql
CREATE DATABASE drf_db;
CREATE USER drf_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE drf_db TO drf_user;
\q

#### Примени миграции
python manage.py migrate

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

## Тестирование

python manage.py test


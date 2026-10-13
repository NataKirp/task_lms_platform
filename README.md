# Платформа онлайн-обучения

REST API для платформы онлайн-обучения на Django REST Framework. Позволяет управлять курсами и уроками, 
оформлять подписки, принимать оплату через Stripe и рассылать уведомления подписчикам.

**Production:** http://45.132.177.136
**Репозиторий:** https://github.com/NataKirp/task_lms_platform.git

## Содержание

- [Возможности](#возможности)
- [Технологии](#технологии)
- [Структура проекта](#структура-проекта)
- [Быстрый старт (Docker)](#быстрый-старт-docker)
- [Локальный запуск (без Docker)](#локальный-запуск-без-docker)
- [Переменные окружения](#переменные-окружения)
- [API](#api)
- [Управляющие команды](#управляющие-команды)
- [Тестирование](#тестирование)
- [Роли и права доступа](#роли-и-права-доступа)
- [CI/CD и деплой](#cicd-и-деплой)

## Возможности

- **Курсы и уроки** — CRUD-операции с разграничением прав по ролям (владелец / модератор / администратор).
- **Подписки на обновления курса** — пользователь может подписаться и получать email-уведомления при изменениях.
- **Оплата курсов через Stripe** — генерация платёжной ссылки, отслеживание статуса платежа.
- **История платежей** — фильтрация и сортировка по способу оплаты, дате, курсу/уроку.
- **JWT-аутентификация** — access + refresh токены (`djangorestframework-simplejwt`).
- **Асинхронные задачи** — рассылка писем и автоматическая деактивация «спящих» пользователей через Celery.
- **OpenAPI-документация** — Swagger UI и ReDoc через `drf-spectacular`.
- **Валидация ссылок** — в уроках разрешены только ссылки на YouTube.
- **Пагинация** — кастомная с ограничением размера страницы.
- **Автоматический деплой** — GitHub Actions → Docker Hub → сервер по SSH.

## Технологии

| Компонент | Версия |
|---|---|
| Python | 3.12 |
| Django | 6.0.7 |
| Django REST Framework | — |
| Gunicorn | — |
| Nginx | 1.27-alpine |
| PostgreSQL | 16 |
| Redis | 7 |
| Celery | 5.6 |
| Poetry | 2.2.1 |
| Stripe SDK | — |
| drf-spectacular | — |
| djangorestframework-simplejwt | — |
| phonenumber-field | — |
| django-filter | — |
| django-celery-beat | — |

## Структура проекта

```
task_lms_platform/
├── .github/
│   └── workflows/
│       └── ci.yml              # test → lint → build → deploy
├── config/                     # Настройки Django
│   ├── __init__.py             # Импорт Celery-приложения
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
├── nginx/                      # Конфигурация Nginx
│   ├── Dockerfile
│   └── nginx.conf
├── users/                      # Пользователи, платежи
│   ├── models.py               # User, Payment
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py          # IsModer, IsOwner, IsAccountOwner
│   ├── services.py             # Интеграция со Stripe
│   ├── tasks.py                # Деактивация неактивных пользователей
│   └── management/commands/fill_db.py
├── materials/                  # Курсы, уроки, подписки
│   ├── models.py               # Course, Lesson, Subscription
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── validators.py           # validate_youtube_only
│   ├── pagination.py
│   ├── schema.py               # OpenAPI-схемы
│   ├── tasks.py                # Рассылка обновлений
│   └── tests.py
├── media/                      # Загруженные файлы (не в git)
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── poetry.lock
├── .env.sample                 # Шаблон переменных окружения
├── .env                        # Локальный файл (в .gitignore)
├── .flake8
├── .gitignore
├── .dockerignore
├── .coveragerc
└── README.md
```

## Быстрый старт (Docker)

### Требования

- Docker Desktop ≥ 20.10
- Docker Compose ≥ 2.20

### Запуск

1. Клонировать репозиторий:
   ```bash
   git clone https://github.com/NataKirp/task_lms_platform.git
   cd task_lms_platform
   ```

2. Создать `.env` на основе `.env.sample` и заполнить значения (см. [Переменные окружения](#переменные-окружения)):
   ```bash
   cp .env.sample .env
   ```

3. Собрать и запустить сервисы:
   ```bash
   docker compose up --build
   ```

   Compose поднимет `db` и `redis` с healthcheck'ами, затем `web`, `celery`, `celery-beat` и `nginx`.

4. Применить миграции и собрать статику:
   ```bash
   docker compose exec web python manage.py migrate --noinput
   docker compose exec web python manage.py collectstatic --noinput
   ```

5. Создать суперпользователя:
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

6. (Опционально) Заполнить БД тестовыми данными:
   ```bash
   docker compose exec web python manage.py fill_db
   ```

7. Открыть сервисы:

   | URL | Назначение |
   |---|---|
   | http://localhost/ | API (через Nginx) |
   | http://localhost/admin/ | Django admin |
   | http://localhost/swagger/ | Swagger UI |
   | http://localhost/redoc/ | ReDoc |
   | http://localhost/schema/ | OpenAPI-схема (raw) |

### Остановка и удаление

```bash
docker compose down       # остановить контейнеры, данные сохранятся
docker compose down -v    # остановить + удалить том с БД (полный сброс)
```

## Локальный запуск (без Docker)

1. Установить зависимости через Poetry:
   ```bash
   poetry install
   poetry shell
   ```

2. Запустить Postgres и Redis (локально или в Docker):
   ```bash
   docker run -d --name lms-db -p 5432:5432 \
     -e POSTGRES_DB=lms -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres \
     postgres:16
   docker run -d --name lms-redis -p 6379:6379 redis:7-alpine
   ```

3. Создать `.env` — `DB_HOST=localhost`, `CELERY_BROKER_URL=redis://127.0.0.1:6379/0`.

4. Применить миграции и запустить сервер:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

5. В отдельных терминалах:
   ```bash
   celery -A config worker -l INFO
   celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
   ```

## API

Все эндпоинты, кроме регистрации и логина, требуют JWT-токен в заголовке:

```
Authorization: Bearer <access_token>
```

### Аутентификация

| Метод | Эндпоинт | Описание |
|---|---|---|
| POST | `/users/` | Регистрация |
| POST | `/users/login/` | Получить пару access + refresh |
| POST | `/users/token/refresh/` | Обновить access по refresh |

**Пример логина:**

```bash
curl -X POST http://45.132.177.136/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "pass"}'
```

### Пользователи

| Метод | Эндпоинт | Описание |
|---|---|---|
| GET | `/users/` | Список пользователей |
| GET | `/users/{id}/` | Профиль (свой — расширенный, чужой — краткий) |
| PATCH | `/users/{id}/` | Редактирование (только свой профиль) |
| DELETE | `/users/{id}/` | Удаление (только свой профиль) |

### Платежи

| Метод | Эндпоинт | Описание |
|---|---|---|
| GET | `/users/payments/` | Список платежей (свой / все для админа) |
| POST | `/users/payments/stripe/` | Создать Stripe-сессию для оплаты курса |
| GET | `/users/payments/{id}/status/` | Проверить актуальный статус платежа в Stripe |

Параметры фильтрации для `/users/payments/`:
- `?payment_method=cash|bank_transfer|stripe`
- `?course_paid=<id>`
- `?single_lesson_paid=<id>`
- `?ordering=-payment_date`

### Курсы

| Метод | Эндпоинт | Описание |
|---|---|---|
| GET | `/materials/courses/` | Список курсов (свои + подписки) |
| POST | `/materials/courses/` | Создать курс |
| GET | `/materials/courses/{id}/` | Детали курса |
| PATCH | `/materials/courses/{id}/` | Обновить курс (уведомляет подписчиков) |
| DELETE | `/materials/courses/{id}/` | Удалить курс |

### Уроки

| Метод | Эндпоинт | Описание |
|---|---|---|
| GET | `/materials/lesson/` | Список уроков |
| POST | `/materials/lesson/create/` | Создать урок |
| GET | `/materials/lesson/{id}/` | Детали урока |
| PATCH | `/materials/lesson/{id}/update/` | Обновить урок |
| DELETE | `/materials/lesson/{id}/delete/` | Удалить урок |

### Подписки

| Метод | Эндпоинт | Описание |
|---|---|---|
| POST | `/materials/course/subscribe/` | Установить / снять подписку (toggle) |

**Тело запроса:**
```json
{ "course_id": 1 }
```

Ответ:
```json
{ "message": "Подписка успешно добавлена" }
```

## Управляющие команды

### `fill_db` — заполнение тестовыми данными

Создаёт пользователей, модератора, суперюзера, курсы, уроки, подписки и платежи.

```bash
docker compose exec web python manage.py fill_db
docker compose exec web python manage.py fill_db --noinput   # без подтверждения
```

**Что удаляется перед наполнением:** `Payment`, `Lesson`, `Course`, `Subscription`, все не-суперюзеры.

**Тестовые аккаунты:**

| Роль | Email | Пароль |
|---|---|---|
| Админ | `admin@example.com` | `adminpass123` |
| Модератор | `moder@example.com` | `testpass123` |
| Пользователи 1–4 | `user{1..4}@example.com` | `testpass123` |

### Другие команды

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py collectstatic --noinput
docker compose exec web python manage.py spectacular --file /tmp/schema.yml  # проверка OpenAPI
```

## Тестирование

```bash
docker compose exec web python manage.py test
# или из poetry-окружения:
poetry run python manage.py test
```

Покрытые сценарии:
- CRUD курсов и уроков владельцем
- Создание урока модератором → 403
- Детальный просмотр урока чужим пользователем → 403
- Подписка: добавление и удаление (toggle)
- Список курсов и уроков с пагинацией

## Роли и права доступа

Проект использует три роли:

| Роль | Определение | Права |
|---|---|---|
| **Администратор** | `is_superuser=True` | Полный доступ ко всему |
| **Модератор** | Состоит в группе `Модераторы` | Видит все курсы и уроки, может редактировать, **не может** создавать и удалять |
| **Пользователь** | Обычный аккаунт | Видит только свои курсы и курсы, на которые подписан; редактирует и удаляет только свои объекты |

Кастомные permissions находятся в `users/permissions.py`:

- `IsModer` — проверяет членство в группе «Модераторы» или `is_superuser`
- `IsOwner` — проверяет, что `obj.owner == request.user`
- `IsAccountOwner` — для редактирования/удаления собственного профиля

## CI/CD и деплой

### Pipeline

Workflow `.github/workflows/ci.yml` запускается на `push` и `pull_request` и проходит четыре стадии:

```
test → lint → build → deploy
```

| Job | Что делает |
|---|---|
| `test` | `python manage.py test` (SQLite, без внешних сервисов) |
| `lint` | Проверка кода через `flake8` |
| `build` | Сборка Docker-образа и push в Docker Hub с тегом `${{ github.sha }}` |
| `deploy` | Только при `push` в `main`: SSH на сервер, `git pull`, миграции, `collectstatic`, `docker compose up -d` |

Каждая стадия зависит от предыдущей через `needs`, ошибка на любом шаге останавливает pipeline.

### Сервер

- **Провайдер:** Cloud.ru, Ubuntu 24.04
- **IP:** `45.132.177.136`
- **Директория проекта:** `/var/www/lms`
- **Пользователь:** `user1`
- **Стек в проде:** Gunicorn (за Nginx), PostgreSQL 16, Redis 7, Celery, Celery Beat

Наружу открыты только порты **22** (SSH) и **80** (HTTP). `web`, `db` и `redis` доступны только внутри docker-сети 
через `expose`.

### GitHub Secrets

Настроены в **Settings → Secrets and variables → Actions**:

| Secret | Назначение |
|---|---|
| `SSH_KEY` | Приватный SSH-ключ для подключения к серверу |
| `SSH_USER` | Имя пользователя на сервере (`user1`) |
| `SERVER_IP` | IP-адрес сервера (`45.132.177.136`) |
| `DEPLOY_DIR` | Путь к директории проекта (`/var/www/lms`) |
| `DOCKER_HUB_USERNAME` | Логин на Docker Hub |
| `DOCKER_HUB_ACCESS_TOKEN` | Access token Docker Hub |

### Переменные окружения на сервере

Файл `/var/www/lms/.env` создаётся вручную и не коммитится. Значения — по образцу `.env.sample`. Для прода:

```env
DEBUG=False
ALLOWED_HOSTS=45.132.177.136
```

### Ручной деплой (если нужно)

```bash
ssh user1@45.132.177.136
cd /var/www/lms

git fetch origin main
git reset --hard origin/main

docker compose pull
docker compose run --rm -T web python manage.py migrate --noinput
docker compose run --rm -T web python manage.py collectstatic --noinput
docker compose up -d --remove-orphans
docker image prune -f

docker compose ps
```

### Локальная сборка образа

```bash
docker build -t <dockerhub-username>/lms:latest .
docker push <dockerhub-username>/lms:latest
```

## Лицензия

Учебный проект. Свободное использование в образовательных целях.
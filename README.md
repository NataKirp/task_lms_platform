# Платформа онлайн-обучения

REST API для платформы онлайн-обучения на Django REST Framework. Позволяет управлять курсами и уроками, оформлять подписки, принимать оплату через Stripe и рассылать уведомления подписчикам.

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

## Технологии

| Компонент | Версия |
|---|---|
| Python | 3.12 |
| Django | 5.2 |
| Django REST Framework | — |
| PostgreSQL | 16 |
| Redis | 7 |
| Celery | 5.6 |
| Poetry | — |
| Stripe SDK | — |
| drf-spectacular | — |
| djangorestframework-simplejwt | — |
| phonenumber-field | — |
| django-filter | — |
| django-celery-beat | — |

## Структура проекта

```
task_lms_platform/
├── config/                 # Настройки Django, celery, urls
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   ├── wsgi.py
│   └── asgi.py
├── users/                  # Пользователи, платежи, аутентификация
│   ├── models.py           # User, Payment
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py      # IsModer, IsOwner, IsAccountOwner
│   ├── services.py         # Интеграция со Stripe
│   ├── tasks.py            # Деактивация неактивных пользователей
│   └── management/commands/fill_db.py
├── materials/              # Курсы, уроки, подписки
│   ├── models.py           # Course, Lesson, Subscription
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── validators.py       # validate_youtube_only
│   ├── pagination.py
│   ├── tasks.py            # Рассылка обновлений
│   └── tests.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── poetry.lock
├── .env.example
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

2. Создать `.env` на основе `.env.example` и заполнить значения (см. [Переменные окружения](#переменные-окружения)).

3. Собрать и запустить сервисы:
   ```bash
   docker compose up --build
   ```

   Compose сам:
   - поднимет `db` и `redis` с healthcheck'ами,
   - выполнит миграции через сервис `migrate`,
   - запустит `web`, `celery`, `celery-beat` **после** успешных миграций.

4. Создать суперпользователя:
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

5. (Опционально) Заполнить БД тестовыми данными:
   ```bash
   docker compose exec web python manage.py fill_db
   ```

6. Открыть сервисы:

   | URL | Назначение |
   |---|---|
   | http://localhost:8000/ | API |
   | http://localhost:8000/admin/ | Django admin |
   | http://localhost:8000/swagger/ | Swagger UI |
   | http://localhost:8000/redoc/ | ReDoc |
   | http://localhost:8000/schema/ | OpenAPI-схема (raw) |

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

## Переменные окружения

Пример `.env.example`:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL
POSTGRES_DB=lms
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Stripe
STRIPE_API_KEY=sk_test_...

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# Email
DEFAULT_FROM_EMAIL=noreply@lms.local
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

> **Важно:** в `.env` для Docker-режима хосты `db` и `redis` — это имена сервисов из `docker-compose.yml`. Для локального запуска используйте `localhost` / `127.0.0.1`.

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
curl -X POST http://localhost:8000/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "pass"}' -k
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

## Лицензия

Учебный проект. Свободное использование в образовательных целях.

---

Если что-то не работает — создайте issue или напишите в обсуждениях репозитория.
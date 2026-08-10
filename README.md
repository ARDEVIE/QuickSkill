# QuickSkill

MVP веб-платформы для быстрого обмена знаниями между студентами: мини-курсы, PDF/видео-материалы, каталог с поиском, связь с автором в Telegram. Backend — Django + Django REST Framework + SimpleJWT, база — PostgreSQL. Подробности архитектуры и распределение ролей — в паспорте проекта.

## Быстрый запуск через Docker (рекомендуется)

Требуется Docker Desktop.

```bash
cp settings/.env.example settings/.env   # если .env ещё нет
docker compose up --build
```

Поднимутся два сервиса: `db` (PostgreSQL 16) и `backend` (Django, миграции применяются автоматически при старте). После старта:

- API + Swagger UI: http://localhost:8000/api/docs/
- Обычные Django-страницы (login/register/profile): http://localhost:8000/auth/
- Админка: http://localhost:8000/admin/ (суперюзера нужно создать вручную, см. ниже)

Создать суперюзера в уже запущенном контейнере:

```bash
docker compose exec backend python manage.py createsuperuser
```

Прогнать тесты внутри контейнера:

```bash
docker compose exec backend python manage.py test
```

Остановить:

```bash
docker compose down       # оставить данные БД
docker compose down -v    # удалить и volume с данными БД/медиа
```

## Локальный запуск без Docker

Нужен установленный и запущенный PostgreSQL (либо просто `docker compose up db` для одной базы, а Django гонять локально).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp settings/.env.example settings/.env   # и поправить POSTGRES_* под свою локальную БД

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

По умолчанию `PROJECT_ENV_ID=dev` (см. `settings/.env`), это переключает `settings/env/dev.py`. Для продакшн-конфигурации используется `settings/env/prod.py` — `ALLOWED_HOSTS` там берётся из `DJANGO_ALLOWED_HOSTS` в `.env` (не хардкожен).

## Переменные окружения

Смотри `settings/.env.example` — там весь список с комментариями по смыслу. Настоящий `.env` в git не попадает.

## Тесты

```bash
python manage.py test          # локально
docker compose exec backend python manage.py test   # в контейнере
```

## API

Полная интерактивная документация — Swagger UI на `/api/docs/` (OpenAPI-схема на `/api/schema/`). Коротко:

| Метод | URL | Доступ |
| --- | --- | --- |
| POST | `/api/auth/register/` | Публичный |
| POST | `/api/auth/login/` | Публичный |
| POST | `/api/auth/refresh/` | Публичный (с refresh-токеном) |
| POST | `/api/auth/logout/` | Авторизован |
| GET/PATCH | `/api/users/me/` | Авторизован |
| GET | `/api/categories/` | Публичный |
| GET | `/api/courses/` | Публичный (черновики видны только автору) |
| POST | `/api/courses/` | Авторизован |
| GET/PATCH/DELETE | `/api/courses/{id}/` | Публичный на чтение, автор на запись |
| POST | `/api/courses/{id}/materials/` | Автор курса |
| POST | `/api/courses/{id}/favorite/` | Авторизован |
| GET/PATCH/DELETE | `/api/materials/{id}/` | Публичный на чтение, автор на запись |

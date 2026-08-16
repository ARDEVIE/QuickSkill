# QuickSkill

MVP веб-платформы для быстрого обмена знаниями между студентами: мини-курсы, PDF/видео-материалы, каталог с поиском, связь с автором в Telegram. Backend — Django + Django REST Framework + SimpleJWT, база — PostgreSQL. Подробности архитектуры и распределение ролей — в паспорте проекта.

## Быстрый запуск через Docker (рекомендуется)

Требуется Docker Desktop.

```bash
./setup.sh
```

Скрипт проверит, что Docker запущен, создаст `backend/settings/.env` из примера (если его ещё нет), соберёт и поднимет `db` + `backend`, дождётся, пока backend ответит, и выведет ссылки.

Вручную, теми же шагами:

```bash
cp backend/settings/.env.example backend/settings/.env   # если .env ещё нет
docker compose up --build
```

Поднимутся два сервиса: `quickskill-db` (PostgreSQL 16) и `quickskill-backend` (Django, миграции применяются автоматически при старте). После старта:

- API + Swagger UI: http://localhost:8000/api/docs/
- Админка: http://localhost:8000/admin/ (суперюзера нужно создать вручную, см. ниже)

Создать суперюзера в уже запущенном контейнере:

```bash
docker compose exec quickskill-backend python manage.py createsuperuser
```

Прогнать тесты внутри контейнера:

```bash
docker compose exec quickskill-backend python manage.py test
```

Остановить:

```bash
docker compose down       # оставить данные БД
docker compose down -v    # удалить и volume с данными БД/медиа
```

## Локальный запуск без Docker

Нужен установленный и запущенный PostgreSQL (либо просто `docker compose up db` для одной базы, а Django гонять локально).

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp settings/.env.example settings/.env   # и поправить POSTGRES_* под свою локальную БД

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

По умолчанию `PROJECT_ENV_ID=dev` (см. `backend/settings/.env`), это переключает `settings/env/dev.py`. Для продакшн-конфигурации используется `settings/env/prod.py` — `ALLOWED_HOSTS` там берётся из `DJANGO_ALLOWED_HOSTS` в `.env` (не хардкожен).

## Переменные окружения

Смотри `backend/settings/.env.example` — там весь список с комментариями по смыслу. Настоящий `.env` в git не попадает.

## Тесты

```bash
cd backend && python manage.py test                            # локально
docker compose exec quickskill-backend python manage.py test    # в контейнере
```

## Деплой

`docker-compose.prod.yml` — отдельный конфиг под требования общего сервера (`esg.kbtu.kz`):

- сервисы названы с префиксом проекта (`quickskill-backend`, `quickskill-db`), а не общими именами;
- порты не публикуются наружу (`expose`, не `ports`) — доступ только изнутри Docker-сети;
- `quickskill-backend` дополнительно подключается к внешней сети `esg-network` (`external: true`), чтобы её видел общий Nginx;
- backend стартует через Gunicorn (`gunicorn settings.wsgi:application`), а не `manage.py runserver`;
- статика раздаётся Gunicorn'ом через WhiteNoise (`collectstatic` запускается автоматически при старте контейнера).

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Перед этим на сервере должна существовать сеть `esg-network` (создаётся один раз девопсами: `docker network create esg-network`) и `backend/settings/.env` с реальными `PROJECT_SECRET_KEY`, `POSTGRES_PASSWORD` и `DJANGO_ALLOWED_HOSTS` — без них `settings/env/prod.py` откажется стартовать.

**Пока не готово к реальному деплою:** `frontend/` (Angular) в репозитории есть, но ещё не собирается и не подключён ни к `docker-compose.prod.yml`, ни к общему Nginx — без этого подключать путь `esg.kbtu.kz/quickskill` нет смысла.

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

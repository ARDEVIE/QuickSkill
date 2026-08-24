# QuickSkill

Веб-платформа для обмена знаниями между студентами: мини-курсы с модулями и
уроками, рейтинги и избранное, форум вопросов и ответов, профили с публичной
страницей автора.

Backend — Django + Django REST Framework + SimpleJWT, база — PostgreSQL.
Frontend — Angular, работает через REST API.

Есть также нативный iOS-клиент (`ios-app/`, SwiftUI) — но это отдельный
демо-MVP **на локальном хранилище** (`@AppStorage`), к backend API он пока не
подключён (см. `ios-app/QuickSkill/README.md`).

## Возможности

- **Курсы** — создание курса с обложкой и модулями (`Section` → `ContentBlock`:
  текст или медиафайл), черновики (`is_published`), редактирование автором,
  рейтинг 1–5 с комментарием, избранное, поиск и фильтрация каталога
  (по категории, минимальному рейтингу, сортировке по рейтингу).
- **Форум** — вопросы и ответы, привязка вопроса к категории, поиск по
  заголовку/содержимому, отметка принятого ответа автором вопроса, избранные
  вопросы.
- **Профиль** — своя информация и редактирование (имя, фамилия, био, Telegram,
  аватар), публичный профиль по username со списком курсов автора.
- **Авторизация** — регистрация, вход, JWT-токены (access/refresh с ротацией и
  блэклистом), сброс пароля.
  > Сброс пароля не отправляет письмо: ссылка с токеном выводится в лог
  > backend-сервера (`print(...)` в `password_reset_views.py`). Для реального
  > email нужно подключить почтовый backend — сейчас это не сделано.

## Tech stack

**Backend:** Django 6, Django REST Framework, djangorestframework-simplejwt
(JWT-аутентификация), drf-spectacular (OpenAPI/Swagger), PostgreSQL
(`psycopg`), django-cors-headers, Pillow (обработка изображений), WhiteNoise
(раздача статики в проде), Gunicorn (прод-сервер).

**Frontend:** Angular 15, TypeScript, RxJS. Без сторонней UI/icon-библиотеки и
без стейт-менеджера — состояние живёт в сервисах поверх `HttpClient`.

**Инфраструктура:** Docker Compose (dev и prod конфиги отдельно), GitHub
Actions CI (только backend: ruff, isort, `manage.py check`, тесты с покрытием).

## Структура проекта

```text
backend/            Django-проект
  apps/
    users/           пользователи, аутентификация, публичный профиль
    courses/         категории, курсы, модули/уроки, рейтинги, избранное
    articles/        форум: вопросы и ответы
    common/          общие миксины/утилиты (пагинация, base-модели)
  settings/          настройки Django (base/conf + env/dev.py, env/prod.py)
frontend/            Angular SPA (страницы курсов, форума, профиля, авторизации)
ios-app/             нативный iOS-демо на локальном хранилище, к API не подключён
docker-compose.yml       локальная разработка (db + backend + frontend)
docker-compose.prod.yml  прод-конфиг (db + backend + frontend, см. раздел «Деплой»)
setup.sh                 однокомандный локальный запуск через Docker
```

## Требования

- Docker Desktop (для запуска через Docker — рекомендуемый способ) **или**
  Python 3.12+ и Node.js 18+ для запуска без Docker.
- PostgreSQL 16, если запускаете backend без Docker.

## Быстрый запуск через Docker (рекомендуется)

```bash
./setup.sh
```

Скрипт проверит, что Docker запущен, создаст `backend/settings/.env` из
примера (если его ещё нет), соберёт и поднимет контейнеры, дождётся ответа
backend и выведет ссылки.

Вручную, теми же шагами:

```bash
cp backend/settings/.env.example backend/settings/.env   # если .env ещё нет
docker compose up --build
```

Поднимаются три сервиса:

| Сервис | Что это | Адрес |
| --- | --- | --- |
| `quickskill-db` | PostgreSQL 16 | `localhost:5432` |
| `quickskill-backend` | Django (миграции применяются автоматически при старте) | http://localhost:8000 |
| `quickskill-frontend` | Angular Dev Server | http://localhost:4200 |

- Swagger UI: http://localhost:8000/api/docs/
- Админка: http://localhost:8000/admin/ (суперюзера нужно создать вручную)

```bash
# суперюзер
docker compose exec quickskill-backend python manage.py createsuperuser

# тесты
docker compose exec quickskill-backend python manage.py test

# остановить
docker compose down       # оставить данные БД
docker compose down -v    # удалить и volume с данными БД/медиа
```

## Локальный запуск без Docker

### Backend

Нужен запущенный PostgreSQL (можно поднять только его: `docker compose up quickskill-db`).

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp settings/.env.example settings/.env   # и поправить POSTGRES_* под свою БД

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

По умолчанию `PROJECT_ENV_ID=dev` (см. `backend/settings/.env`) — переключает
`settings/env/dev.py`. Для прод-конфигурации используется `settings/env/prod.py`
(`ALLOWED_HOSTS` берётся из `DJANGO_ALLOWED_HOSTS`, статика — через WhiteNoise).

### Frontend

```bash
cd frontend
npm install
npm run start
```

Откроется на http://localhost:4200 и обращается к API на
`http://localhost:8000/api` (см. `frontend/src/environments/environment.ts`).

## Переменные окружения

Список — в `backend/settings/.env.example`. Настоящий `.env` в git не попадает.

| Переменная | Обязательна | По умолчанию | Назначение |
| --- | --- | --- | --- |
| `PROJECT_SECRET_KEY` | да (в проде) | пример-ключ в `.env.example` | Django `SECRET_KEY`. В `.env.example` лежит стандартный `django-insecure-...` ключ — годится только для локальной разработки, для прода обязательно свой. |
| `PROJECT_ENV_ID` | нет | `dev` | `dev` или `prod` — выбирает `settings/env/dev.py` или `settings/env/prod.py`. |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | да | `quickskill` / `quickskill` / `change-me` | Подключение к PostgreSQL. |
| `POSTGRES_HOST` / `POSTGRES_PORT` | нет | `localhost` / `5432` | В Docker Compose переопределяются на `quickskill-db` / `5432`. |
| `DJANGO_ALLOWED_HOSTS` | да (в проде) | `localhost,127.0.0.1` | `ALLOWED_HOSTS`, читается только в `env/prod.py`; без него прод не стартует. |
| `CORS_ALLOWED_ORIGINS` | нет | `http://localhost:4200,http://127.0.0.1:4200` | Список источников для CORS. Есть в коде (`settings/conf.py`), но отсутствует в `.env.example` — переопределяйте вручную, если фронтенд крутится на другом адресе. |

## API

Полная интерактивная документация — Swagger UI на `/api/docs/` (OpenAPI-схема
на `/api/schema/`). Основные группы эндпоинтов:

| Группа | Примеры |
| --- | --- |
| Auth | `POST /api/auth/register/`, `/login/`, `/refresh/`, `/logout/`, `/password-reset/`, `/password-reset-confirm/` |
| Пользователи | `GET/PATCH /api/users/me/`, `GET /api/users/me/favorites/`, `GET /api/users/{username}/` |
| Категории | `GET /api/categories/` |
| Курсы | `GET/POST /api/courses/`, `GET/PATCH/DELETE /api/courses/{id}/`, `POST /api/courses/{id}/favorite/`, `GET/POST /api/courses/{id}/ratings/` |
| Модули/уроки | `POST /api/courses/{id}/sections/`, `GET/PATCH/DELETE /api/sections/{id}/`, `POST /api/sections/{id}/blocks/`, `GET/PATCH/DELETE /api/blocks/{id}/` |
| Форум | `GET/POST /api/questions/`, `GET/PATCH/DELETE /api/questions/{slug}/`, `GET/POST /api/questions/{slug}/comments/`, `POST /api/questions/{slug}/favorite/`, `POST /api/questions/{slug}/accept_answer/`, `PATCH/DELETE /api/comments/{id}/` |

Доступ на чтение в основном публичный (`AllowAny`), запись требует JWT
(`Authorization: Bearer <access_token>`); черновики курсов видны только автору.

## Тесты

```bash
cd backend && python manage.py test                            # локально
docker compose exec quickskill-backend python manage.py test    # в контейнере
```

Frontend: `cd frontend && npm test` (Karma/Jasmine). CI эти тесты не
прогоняет — `.github/workflows/ci.yml` покрывает только backend (lint + tests).

## Деплой

`docker-compose.prod.yml` — отдельный конфиг под требования общего сервера
(`esg.kbtu.kz`):

- сервисы названы с префиксом проекта (`quickskill-backend`, `quickskill-db`,
  `quickskill-frontend`) — на общей Docker-сети `esg-network` крутятся сразу
  несколько проектов, поэтому общие имена (`backend`, `frontend`, `db`)
  запрещены;
- порты не публикуются наружу (`expose`, не `ports`) — доступ только изнутри
  Docker-сети;
- `quickskill-backend` и `quickskill-frontend` дополнительно подключаются к
  внешней сети `esg-network` (`external: true`), чтобы их видел общий
  (Public) Nginx; `quickskill-db` — только на внутренней сети проекта;
- backend стартует через Gunicorn (`gunicorn settings.wsgi:application`), а
  не `manage.py runserver`;
- статика раздаётся Gunicorn'ом через WhiteNoise (`collectstatic` запускается
  автоматически при старте контейнера);
- `quickskill-frontend` — свой внутренний Nginx (`frontend/Dockerfile.prod` +
  `frontend/nginx.conf`): multi-stage сборка Angular (`ng build --base-href`)
  и раздача собранного SPA, с проксированием `/api/`, `/admin/`, `/static/`,
  `/media/` на `quickskill-backend:8000`. Внутренний Nginx ничего не знает про
  префикс проекта (`/quickskill`) — `location`-блоки написаны так, будто
  проект живёт в корне сайта; добавлением префикса на сервере занимается
  общий Public Nginx.
- путь, под которым проект будет доступен на `esg.kbtu.kz` (например,
  `esg.kbtu.kz/quickskill/`), задаётся Angular через `<base href>` на этапе
  сборки — build-arg `BASE_HREF` в `docker-compose.prod.yml` (по умолчанию
  `/quickskill/`, при необходимости меняется под фактически выданный путь).

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Перед этим на сервере должна существовать сеть `esg-network` (создаётся один
раз: `docker network create esg-network`) и `backend/settings/.env` с
реальными `PROJECT_SECRET_KEY`, `POSTGRES_PASSWORD` и `DJANGO_ALLOWED_HOSTS` —
без них `settings/env/prod.py` откажется стартовать.

## Troubleshooting

- **Backend не отвечает после `docker compose up`** — смотрите логи:
  `docker compose logs quickskill-backend`. Частая причина — БД ещё не готова
  (healthcheck) или `.env` не создан из примера.
- **`ImproperlyConfigured` при старте в проде** — не заданы
  `PROJECT_SECRET_KEY` и/или `POSTGRES_PASSWORD` в `.env`; в dev-режиме это
  не проверяется.
- **CORS-ошибки во фронтенде на нестандартном порту/домене** — задайте
  `CORS_ALLOWED_ORIGINS` в `.env` (по умолчанию разрешён только
  `localhost:4200`).

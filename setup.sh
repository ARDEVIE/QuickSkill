#!/usr/bin/env bash
# One-command bootstrap: clone the repo, run this, get a working QuickSkill locally.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

info() { printf '\033[1;34m==>\033[0m %s\n' "$1"; }
warn() { printf '\033[1;33m!!\033[0m %s\n' "$1"; }
die() {
    printf '\033[1;31mError:\033[0m %s\n' "$1" >&2
    exit 1
}

command -v docker >/dev/null 2>&1 || die "Docker не найден. Установите Docker Desktop: https://www.docker.com/products/docker-desktop/"
docker compose version >/dev/null 2>&1 || die "Плагин 'docker compose' не найден (нужен Docker Desktop свежей версии)."
docker info >/dev/null 2>&1 || die "Docker демон не запущен. Откройте Docker Desktop и повторите запуск."

if [ ! -f settings/.env ]; then
    info "settings/.env не найден, создаю из settings/.env.example"
    cp settings/.env.example settings/.env
else
    info "settings/.env уже есть, не трогаю"
fi

info "Собираю и поднимаю quickskill-db + quickskill-backend (docker compose up --build)"
docker compose up --build -d

info "Жду, пока backend ответит на /api/docs/ (миграции применяются автоматически)"
ready=false
for _ in $(seq 1 30); do
    if curl -fs http://localhost:8000/api/docs/ >/dev/null 2>&1; then
        ready=true
        break
    fi
    sleep 2
done

if [ "$ready" != true ]; then
    warn "Backend не ответил за 60 секунд. Смотрите логи: docker compose logs quickskill-backend"
    exit 1
fi

cat <<'EOF'

Готово! QuickSkill поднят локально:

  Swagger UI (JWT API):     http://localhost:8000/api/docs/
  Django-страницы (сессия): http://localhost:8000/auth/
  Админка:                  http://localhost:8000/admin/

Суперпользователя ещё нет, создать:
  docker compose exec quickskill-backend python manage.py createsuperuser

Прогнать тесты:
  docker compose exec quickskill-backend python manage.py test

Остановить:
  docker compose down          # оставить данные БД
  docker compose down -v       # снести и данные БД/медиа
EOF

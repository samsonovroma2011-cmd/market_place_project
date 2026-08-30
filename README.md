# 🛒 Market Place — пет-проект на FastAPI

Учебный проект: интернет-магазин на современном асинхронном стеке.

## Стек

| Компонент | Технология |
|-----------|------------|
| API | FastAPI + Pydantic v2 |
| БД | PostgreSQL 16, SQLAlchemy 2.0 (async, asyncpg) |
| Миграции | Alembic |
| Кэш и брокер | Redis 7 |
| Фоновые задачи | Celery (+ Beat) |
| Контейнеры | Docker Compose |

## Структура

Подробная архитектура и все принятые решения — в [ARCHITECTURE.md](ARCHITECTURE.md).

## Запуск

```bash
cp .env.example .env
docker compose up --build
# Swagger: http://localhost:8000/docs
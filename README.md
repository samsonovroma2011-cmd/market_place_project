# 🛒 Shop API — пет-проект на FastAPI

Учебный проект: интернет-магазин, построенный на современном асинхронном стеке.

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
```

## Дорожная карта

- [ ] M0 — каркас проекта
- [ ] M1 — модели и миграции
- [ ] M2 — аутентификация (JWT)
- [ ] M3 — каталог + кэш Redis
- [ ] M4 — корзина
- [ ] M5 — заказы и транзакции
- [ ] M6 — Celery-уведомления
- [ ] M7 — отчёты (Celery Beat)
- [ ] M8 — тесты и полировка

## Лицензия

MIT (укажи автора)

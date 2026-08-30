# 🛒 Интернет-магазин — архитектура пет-проекта

**Стек:** FastAPI · SQLAlchemy 2.0 (async) · PostgreSQL · Redis · Celery · Alembic · Docker Compose

---

## 1. Цель и объём (MVP)

**Входит:**
- Каталог: категории, товары (цена, скидка, остатки), фильтры, пагинация, поиск
- Аутентификация: регистрация, вход, JWT (access + refresh), профиль
- Корзина: добавление/изменение/удаление позиций, итоговая сумма
- Заказы: создание из корзины, статусы, списание остатков, имитация оплаты
- Уведомления (Celery): письма о регистрации, подтверждение заказа, об оплате
- Отчёты (Celery Beat): ежедневный отчёт по продажам (Excel/CSV) на почту
- Кэш каталога в Redis
- Инфраструктура: Docker Compose (api, worker, beat, postgres, redis, mailhog, flower)

**Не входит (осознанно):**
- Реальная оплата — делаем абстракцию `PaymentProvider` с фейковой реализацией
- Фронтенд — только API (Swagger в роли клиента)
- Админка — при желании докрутим отдельным модулем

> Правило: функциональность добавляем, только если она требует нового архитектурного
> решения (новая таблица, новый слой, новый паттерн). Всё остальное — в «потом».

---

## 2. Функциональные модули

Feature-based раскладка: каждый модуль = свой набор моделей, схем, сервиса и роутера.

| Модуль        | Отвечает за                                        | Специфика                        |
|---------------|----------------------------------------------------|---------------------------------|
| `auth`        | регистрация, логин, JWT, refresh                   | security, зависимости           |
| `catalog`     | категории, товары, фильтры, поиск, остатки         | кэш в Redis                     |
| `cart`        | корзина (PostgreSQL, см. 5.9)                      | FK, дёшево обновляется          |
| `orders`      | заказ, статусы, списание остатков                  | транзакции, `FOR UPDATE`        |
| `payments`    | абстракция платёжного шлюза, имитация оплаты       | idempotency                     |
| `notifications` | e-mail уведомления                               | Celery-задачи, retries          |
| `reports`     | агрегация продаж, выгрузка файла, отправка почтой  | Celery Beat, тяжёлый расчёт     |

---

## 3. Слои и правила

```
HTTP → api/ (роутеры + Pydantic-схемы) → services/ (бизнес-логика) → models/ (SQLAlchemy)
                                                            │
                                                            └→ tasks/ (Celery)
```

**Железные правила (нарушать нельзя):**
1. Роутер не знает про SQLAlchemy. Он получает/отдаёт Pydantic-схемы и дергает сервис.
2. Сервис не знает про HTTP. Исключение — сигнатуры `return HTTPException` через raise,
   но try/except на HTTP-коды живёт в роутере.
3. Транзакции — только в сервисе. Один сервисный метод = одна бизнес-операция.
4. Слой репозиториев намеренно **не добавляем**: для пет-проекта это чаще overengineering.
   Если потом захочется — вынесем точечно, без переписывания.
5. Кэш — за сервисом (кэшируем результат доменной операции, не «кусок JSON»).

---

## 4. Структура проекта

```
shop-api/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── pyproject.toml                # uv/pip; зависимости сгруппированы: dev, api, worker
├── alembic.ini
├── alembic/
│   ├── env.py                    # async-движок, autogenerate
│   └── versions/
├── app/
│   ├── main.py                   # FastAPI, lifespan (pool'ы), подключение роутеров
│   ├── core/
│   │   ├── config.py             # pydantic-settings, все настройки из .env
│   │   ├── db.py                 # async engine + async_sessionmaker
│   │   ├── redis.py              # redis.asyncio, пул
│   │   ├── celery_app.py         # инстанс Celery (broker=Redis)
│   │   ├── security.py           # hash паролей, JWT-хелперы
│   │   └── logging.py            # структурированный лог
│   ├── db/
│   │   ├── base.py               # DeclarativeBase + миксины (id, created_at, updated_at)
│   │   └── session.py            # get_db() зависимость
│   ├── models/                   # SQLAlchemy 2.0, Mapped[]/mapped_column
│   │   ├── user.py  category.py  product.py  order.py  order_item.py
│   ├── schemas/                  # Pydantic v2: request/response отдельно
│   ├── api/
│   │   ├── deps.py               # get_current_user, pagination
│   │   └── v1/
│   │       ├── router.py         # агрегатор
│   │       ├── auth.py  catalog.py  cart.py  orders.py  reports.py
│   ├── services/
│   │   ├── auth_service.py  product_service.py  cart_service.py
│   │   ├── order_service.py  report_service.py
│   ├── tasks/                    # Celery
│   │   ├── notifications.py      # письма
│   │   └── nightly.py            # отчёты, напоминания о корзине
│   └── utils/email.py            # SMTP-клиент (в dev — console/MailHog)
└── tests/                        # pytest + httpx AsyncClient
```

---

## 5. Ключевые архитектурные решения

### 5.1 Async в API, sync в Celery-воркере
API работает через `asyncpg` + `AsyncSession`. Celery-воркер — **отдельный процесс**,
и там мы держим **второй, синхронный** движок (`psycopg`):
- письма/отчёты — IO-bound, но почти все библиотеки (openpyxl, smtplib) синхронные;
- упрощает ретраи и отладку задач;
- `asgiref.async_to_sync`-обёртки не нужны, единый стиль `def task()`.
> Это нормальная практика, а не «костыль». Оба движка смотрят в одну БД.

### 5.2 Остатки без гонок — `SELECT ... FOR UPDATE`
Создание заказа — одна транзакция:
1. `SELECT ... WHERE product_id IN (...) FOR UPDATE` → блокируем строки товаров;
2. проверяем и списываем остатки (меньше 0 → откат, 409);
3. создаём `Order` + `OrderItem`, считаем сумму на стороне БД/сервиса;
4. коммит.
Это самый «интервьюшный» момент проекта — про блокировки и уровень изоляции.

### 5.3 Кэш каталога с версионированием
- Ключи: `catalog:products:{category}:{page}:{sort}` + TTL 5–10 мин;
- при изменении товара/категории инкрементируем `catalog:version` в Redis — старые ключи
  перестают читаться (cache-aside с версией вместо хрупкой точечной инвалидации);
- на чтение: Redis → промах → БД → запись в кэш.

### 5.4 Celery: надёжность
- Каждой задаче — `max_retries`/`backoff`, **идемпотентность** (повторная отправка
  письма о заказе `order_id=42` не отправит второе — проверка статуса в БД);
- «брошенная корзина» — Beat-задача раз в N часов: нашла корзины без заказа → письмо;
- нерелевантные ошибки (SMTP упал) обрабатываются ретраями, бизнес-ошибки — терминально.

### 5.5 Аутентификация
- JWT: access ~30 мин, refresh ~30 дней (с ротацией), хранение hash пароля — bcrypt/argon2;
- `get_current_user` — зависимость с кэшем профиля в Redis (TTL 60 сек) или без кэша на MVP;
- refresh-токены в Redis для отзыва (черный список при logout) — хороший кейс Redis.

### 5.9 Корзина в PostgreSQL — решение зафиксировано ✅
Таблица `cart_items`: `user_id` (FK), `product_id` (FK), `quantity`, `created_at`, `updated_at`,
уникальный индекс `(user_id, product_id)` — один товар = одна строка (обновляем `quantity`).
- Сумма/итог — обычный `JOIN` с товарами в одной транзакции чтения;
- консистентность и FK — бесплатно; никаких «слетевших» корзин;
- честный ответ на собеседовании: «в продакшене с высокой нагрузкой корзину выносят в Redis
  для скорости, но в нашем проекте она в Postgres, потому что это бизнес-данные».
- Redis закрывает другие роли: кэш каталога, брокер Celery, blacklist refresh-токенов.

### 5.10 Конфиг и окружение
`pydantic-settings`: один объект настроек, `.env.example` в репо, секреты — только в env.
Валидация на старте (упасть сразу, а не на первом запросе).

### 5.7 Письма в разработке
В compose поднимаем **MailHog** — письма «приходят» в веб-интерфейс, SMTP не нужен.

### 5.8 Мониторинг задач
**Flower** в compose: видно очереди, задачи, ретраи. Бесплатно и наглядно для демо.

---

## 6. Ключевые потоки

### Создание заказа (checkout)
```
POST /orders  (Authorization: Bearer)
  → cart_service: читаем корзину из PostgreSQL (JOIN с товарами)
  → order_service.create_order():
       транзакция
         ├─ SELECT ... FOR UPDATE (товары)
         ├─ проверка остатков / цены (цена берётся из БД, не из клиента!)
         ├─ INSERT orders, order_items
         └─ COMMIT
  → celery: send_order_confirmation.delay(order_id)   ← не ждём в HTTP
  → 201 + статус "pending"
```

### Оплата (имитация)
```
POST /orders/{id}/pay
  → payments: переводит заказ pending → paid (идемпотентно)
  → celery: send_payment_receipt.delay(order_id)
```

### Ночной отчёт
```
Celery Beat (07:00) → generate_daily_report.delay()
  → агрегаты продаж за вчера (SQL по orders/order_items)
  → openpyxl → файл в /tmp
  → email с вложением (MailHog/SMTP)
```

---

## 7. Дорожная карта

| Этап | Содержание | Критерий готовности |
|------|-----------|---------------------|
| **M0** | Каркас: структура, Docker Compose, config, healthcheck, Alembic | `docker compose up` → `/health` → Swagger |
| **M1** | Модели + миграции: users, categories, products | autogenerate, `alembic upgrade head` без ошибок |
| **M2** | Auth: регистрация, логин, JWT, `get_current_user` | полный цикл в Swagger, `401` на закрытом руте |
| **M3** | Каталог: list/detail, пагинация, фильтры, кэш Redis | второй запрос быстрее первого (лог cache hit) |
| **M4** | Корзина: `cart_items`, CRUD, итог | CRUD корзины, сумма, join с товарами |
| **M5** | Заказы: checkout-транзакция, остатки, статусы, имитация оплаты | гонки исключены (тест параллельных заказов) |
| **M6** | Celery: письма (регистрация, заказ, оплата), ретраи | письма в MailHog, Flower видит задачи |
| **M7** | Beat: ежедневный отчёт Excel на почту | отчёт с данными в почте |
| **M8** | Полировка: rate-limit, тесты, README | `pytest` зелёный, README с запуском |

Каждый этап = короткий спринт: обсудили → ты пишешь → я ревьюю и объясняю, где можно было иначе.

---

## 8. Принятые решения

| # | Решение | Статус |
|---|---------|--------|
| 1 | Корзина в PostgreSQL (`cart_items`, FK, unique `(user_id, product_id)`) | ✅ принято |
| 2 | Корзина только у авторизованных (гостевая — потенциальный апгрейд) | ✅ принято |
| 3 | Формат отчёта: Excel (openpyxl), PDF — опционально позже | ⏳ уточнить |

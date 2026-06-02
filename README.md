# Payment Processing Service

Сервис для создания и обработки платежей.

## Требования

* Docker
* Docker Compose

## Настройка

Создайте файл `.env`:

```env
API_KEY=your_api_key

POSTGRES_DB=payments
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

## Запуск

```bash
docker compose up --build
```

## Миграции

Применить миграции:

```bash
uv run alembic upgrade head
```

Создать миграцию:

```bash
uv run alembic revision --autogenerate -m "migration_name"
```

## API

### Создание платежа

```http
POST /api/v1/payments
```

### Получение информации о платеже

```http
GET /api/v1/payments/{payment_id}
```

## Архитектура

```text
Client
  │
  ▼
FastAPI
  │
  ▼
PostgreSQL (Payments + Outbox)
  │
  ▼
Outbox Worker
  │
  ▼
RabbitMQ
  │
  ▼
Consumer
  │
  ▼
Webhook Worker
  │
  ▼
External Webhook
```

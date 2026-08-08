# MVP Foundation - Architecture v0.4

## Обзор

Этот документ описывает фундаментальные компоненты CryptoBroker MVP, реализованные в соответствии с архитектурными ограничениями.

## Архитектурные принципы

### 1. Financial Ledger (Двойная запись)
- **Никаких `user.balance` в таблицах**
- Баланс вычисляется ТОЛЬКО через агрегацию `ledger_entries`
- Каждая операция записывается как entry с типом (DEPOSIT, EXCHANGE, FEE, WITHDRAWAL)
- Поле `balance_after` хранит running balance для оптимизации查询

### 2. State Machine для ордеров
Строгий паттерн state machine управляет переходами статусов:

```
CREATED -> QUOTED -> AWAITING_PAYMENT -> EXECUTING -> SETTLED (terminal)
     |          |            |              |
     v          v            v              v
   FAILED    FAILED      FAILED        FAILED (terminal)
```

Переходы валидируются в `OrderService.transition_state()`.

### 3. Provider Abstraction
Весь код работы с биржами скрыт за интерфейсом `LiquidityProvider`:

```python
class LiquidityProvider(Protocol):
    async def get_quote(...) -> ProviderQuote: ...
    async def execute(order_id: str) -> str: ...
```

MVP использует `SimulatedProvider` для testnet.

### 4. Domain-Driven Design
Слои архитектуры:
```
API (FastAPI routes) 
  -> Service (Domain Services) 
    -> Domain (Models + Business Logic) 
      -> Repository (SQLAlchemy)
```

**Запрещено:** SQL-запросы или вызовы API бирж напрямую из роутов.

### 5. Безопасность
- Никаких секретов в коде
- Pydantic v2 для строгой валидации
- Secrets загружаются из environment variables

## Структура модулей

### Models (`app/models/`)
- `User` — связь с Telegram (telegram_id, username, kyc_status)
- `Company` — B2B сущность с CompanyMember
- `Asset` / `Network` — справочники крипты и сетей
- `LedgerEntry` — двойная запись (amount, entry_type, reference)
- `Order` — статусы OrderStatus, state machine
- `Quote` — временные котировки (30 сек)

### Services (`app/services/`)
- `QuoteService` — создание и управление котировками
- `OrderService` — lifecycle ордеров с state machine
- `LedgerService` — double-entry bookkeeping

### Providers (`app/providers/`)
- `LiquidityProvider` — Protocol интерфейс
- `SimulatedProvider` — заглушка для MVP

## Миграции Alembic

Initial migration (`0001_initial.py`) создаёт все таблицы:
1. networks, assets, asset_networks
2. companies, company_members
3. users
4. orders (с enum orderstatus)
5. ledger_entries (с enum ledgerentrytype)

## Запуск локально

```bash
# Установка зависимостей
cd apps/api
pip install -r requirements.txt

# Запуск миграций
alembic upgrade head

# Запуск API
uvicorn app.main:app --reload
```

## Следующие шаги

После утверждения фундамента:
1. API endpoints для quotes и orders
2. Telegram Bot integration (aiogram 3)
3. Celery workers для фоновых задач
4. Frontend (Next.js Mini App + Admin)

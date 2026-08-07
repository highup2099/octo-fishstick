# CryptoBroker — Architecture v0.4

Development bootstrap for a compliance-first Telegram Mini App crypto brokerage.

## Included

- FastAPI + SQLAlchemy + PostgreSQL
- Redis + Celery worker
- aiogram Telegram bot
- Next.js Mini App
- Next.js admin panel
- Alembic migration
- Simulated liquidity provider
- Quote engine
- Order state machine
- Initial ledger schema
- Docker Compose
- pytest
- GitHub Actions

**Live exchange trading is disabled.**

## Start

```bash
cp .env.example .env
docker compose up --build
```

API: http://localhost:8000/health  
Swagger: http://localhost:8000/docs  
Mini App: http://localhost:3000  
Admin: http://localhost:3001

## Test

```bash
docker compose run --rm api pytest
```

This repository is an engineering bootstrap, not a production exchange. Before real funds are handled, add legal/regulatory approval, KYC/KYB/KYT integrations, signed webhooks, idempotency, double-entry accounting, reconciliation, secrets management, MFA, security testing and operational controls.

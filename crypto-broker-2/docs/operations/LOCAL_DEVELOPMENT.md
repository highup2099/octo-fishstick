# Local development

1. `cp .env.example .env`
2. Keep `PROVIDER_MODE=simulated`
3. Keep `LIVE_TRADING_ENABLED=false`
4. `docker compose up --build`
5. Open API, Mini App and Admin.

Never commit `.env` or exchange credentials.

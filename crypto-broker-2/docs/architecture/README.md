# Architecture v0.4

The bootstrap separates API/domain, workers, Telegram, Mini App, admin and provider adapters.

The simulated provider is deliberately used first. OKX/Bybit adapters should implement the same provider abstraction and remain disabled until compliance and operational controls are ready.

Live execution gate:

`LIVE_TRADING_ENABLED=false`

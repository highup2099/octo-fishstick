# Security Audit Log Schema

This document describes the audit logging format for financial operations.

## Log Format

All financial operations are logged with the following structure:

```json
{
  "timestamp": "ISO 8601 timestamp",
  "event_type": "quote_created|order_created|order_executed|order_cancelled|funds_deposited|funds_withdrawn",
  "user_id": "UUID",
  "entity_id": "UUID (quote_id, order_id, etc.)",
  "details": {
    "sell_asset": "Asset code",
    "buy_asset": "Asset code",
    "sell_amount": "Decimal amount",
    "buy_amount": "Decimal amount",
    "fee_amount": "Decimal amount",
    "status": "current status"
  },
  "ip_address": "Client IP (if available)",
  "user_agent": "Client user agent (if available)"
}
```

## Logged Events

### Quote Operations
- **quote_created**: When a new quote is generated
  - Includes: sell_asset, buy_asset, sell_amount, buy_amount, fee_amount, provider

### Order Operations
- **order_created**: When an order is created from a quote
  - Includes: quote_id, user_id verification
- **order_executed**: When an order is executed
- **order_cancelled**: When an order is cancelled
- **order_failed**: When an order fails

### Fund Operations
- **funds_deposited**: When funds are deposited
- **funds_withdrawn**: When funds are withdrawn

## Implementation Notes

1. All logs are written to the application log at INFO level
2. Failed operations are logged at ERROR level
3. Logs should be shipped to a secure, tamper-evident storage in production
4. Retention policy: minimum 7 years for compliance

## Rate Limiting

Rate limits are enforced per IP address:
- Quotes: 30 requests per minute
- Orders: 10 requests per minute

Exceeded rate limits return HTTP 429 Too Many Requests.

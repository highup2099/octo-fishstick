from enum import Enum

class OrderState(str, Enum):
    CREATED = "created"
    RISK_CHECK = "risk_check"
    AWAITING_FUNDS = "awaiting_funds"
    EXECUTING = "executing"
    SETTLING = "settling"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

ALLOWED_TRANSITIONS = {
    OrderState.CREATED: {OrderState.RISK_CHECK, OrderState.CANCELLED},
    OrderState.RISK_CHECK: {OrderState.AWAITING_FUNDS, OrderState.BLOCKED, OrderState.FAILED},
    OrderState.AWAITING_FUNDS: {OrderState.EXECUTING, OrderState.CANCELLED, OrderState.FAILED},
    OrderState.EXECUTING: {OrderState.SETTLING, OrderState.FAILED},
    OrderState.SETTLING: {OrderState.COMPLETED, OrderState.FAILED},
    OrderState.COMPLETED: set(),
    OrderState.FAILED: set(),
    OrderState.BLOCKED: set(),
    OrderState.CANCELLED: set(),
}

def transition(current: OrderState, target: OrderState) -> OrderState:
    if target not in ALLOWED_TRANSITIONS[current]:
        raise ValueError(f"Invalid order transition: {current} -> {target}")
    return target

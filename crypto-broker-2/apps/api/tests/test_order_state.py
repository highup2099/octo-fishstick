import pytest
from app.services.order_service import OrderState, transition

def test_valid_transition():
    assert transition(OrderState.CREATED, OrderState.RISK_CHECK) == OrderState.RISK_CHECK

def test_invalid_transition():
    with pytest.raises(ValueError):
        transition(OrderState.CREATED, OrderState.COMPLETED)

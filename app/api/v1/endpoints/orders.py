"""Orders endpoint: thin controller — validate input, call service, return response."""

from fastapi import APIRouter, HTTPException

from app.models.order import OrderCreate, OrderResponse
from app.services import order as order_service
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("", response_model=OrderResponse)
def create_order(data: OrderCreate) -> OrderResponse:
    """Create a new order."""
    return order_service.create_order(data)


@router.get("", response_model=list[OrderResponse])
def list_orders() -> list[OrderResponse]:
    """List all orders."""
    return order_service.list_orders()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str) -> OrderResponse:
    """Get an order by id."""
    order = order_service.get_order(order_id)
    if order is None:
        logger.info("Order not found order_id=%s", order_id)
        raise HTTPException(status_code=404, detail="Order not found")
    return order

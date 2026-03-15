"""Order service: business logic for orders."""

from app.models.order import OrderCreate, OrderResponse
from app.repositories import order as order_repository
from app.utils.logging import get_logger

logger = get_logger(__name__)


def create_order(data: OrderCreate) -> OrderResponse:
    """Create an order (delegate to repository)."""
    logger.info("Creating order item=%r quantity=%s", data.item, data.quantity)
    try:
        order = order_repository.create_order(data)
        logger.info("Order created id=%s", order.id)
        return order
    except Exception as exc:
        logger.exception("Create order failed: %s", exc)
        raise


def get_order(order_id: str) -> OrderResponse | None:
    """Get an order by id."""
    return order_repository.get_order(order_id)


def list_orders() -> list[OrderResponse]:
    """List all orders."""
    return order_repository.list_orders()

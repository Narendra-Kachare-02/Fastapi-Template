"""Order repository: data access for orders (in-memory sample)."""

from app.models.order import OrderCreate, OrderResponse

# In-memory store for demo; replace with DB client in production.
_orders: dict[str, OrderResponse] = {}
_next_id = 1


def create_order(data: OrderCreate) -> OrderResponse:
    """Persist an order and return it."""
    global _next_id
    order_id = str(_next_id)
    _next_id += 1
    order = OrderResponse(id=order_id, item=data.item, quantity=data.quantity)
    _orders[order_id] = order
    return order


def get_order(order_id: str) -> OrderResponse | None:
    """Return an order by id or None."""
    return _orders.get(order_id)


def list_orders() -> list[OrderResponse]:
    """Return all orders."""
    return list(_orders.values())

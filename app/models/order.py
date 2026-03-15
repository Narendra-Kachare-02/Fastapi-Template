"""Order domain models."""

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    """Input for creating an order."""

    item: str = Field(..., min_length=1, description="Order item name")
    quantity: int = Field(..., ge=1, description="Quantity")


class OrderResponse(BaseModel):
    """Order as returned by the API."""

    id: str
    item: str
    quantity: int

    model_config = {"from_attributes": True}

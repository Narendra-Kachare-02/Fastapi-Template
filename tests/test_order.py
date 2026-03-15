"""Tests for order endpoint and service."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_order() -> None:
    """POST /api/v1/orders creates an order."""
    response = client.post(
        "/api/v1/orders",
        json={"item": "Widget", "quantity": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["item"] == "Widget"
    assert data["quantity"] == 2
    assert "id" in data


def test_list_orders() -> None:
    """GET /api/v1/orders returns list of orders."""
    response = client.get("/api/v1/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_order_not_found() -> None:
    """GET /api/v1/orders/nonexistent returns 404."""
    response = client.get("/api/v1/orders/nonexistent-id-999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"

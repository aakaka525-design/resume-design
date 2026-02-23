from datetime import datetime, timezone
from typing import Dict, Set


class PaymentStore:
    """In-memory payment callback simulation for idempotency evidence."""

    def __init__(self) -> None:
        self.orders: Dict[str, dict] = {}
        self.processed_callbacks: Set[str] = set()

    def create_order(self, order_id: str, amount_cents: int) -> dict:
        if order_id in self.orders:
            raise ValueError(f"order already exists: {order_id}")
        self.orders[order_id] = {
            "order_id": order_id,
            "amount_cents": amount_cents,
            "status": "PENDING",
            "paid_at": None,
        }
        return self.orders[order_id]

    def handle_callback(
        self,
        *,
        order_id: str,
        callback_id: str,
        event: str,
        paid_amount_cents: int,
    ) -> dict:
        if callback_id in self.processed_callbacks:
            order = self.orders.get(order_id, {"status": "UNKNOWN"})
            return {"status": "IGNORED_DUPLICATE", "order_status": order["status"]}

        order = self.orders.get(order_id)
        if order is None:
            return {"status": "ORDER_NOT_FOUND", "order_id": order_id}

        if event == "PAY_SUCCESS":
            if paid_amount_cents != order["amount_cents"]:
                return {
                    "status": "REJECTED_AMOUNT_MISMATCH",
                    "expected_amount_cents": order["amount_cents"],
                    "paid_amount_cents": paid_amount_cents,
                }
            if order["status"] == "CANCELLED":
                return {"status": "REJECTED_CONFLICT", "reason": "order_cancelled"}
            if order["status"] == "PAID":
                self.processed_callbacks.add(callback_id)
                return {"status": "IGNORED_ALREADY_PAID", "order_id": order_id}

            order["status"] = "PAID"
            order["paid_at"] = datetime.now(timezone.utc).isoformat()
            self.processed_callbacks.add(callback_id)
            return {"status": "PAID", "order_id": order_id}

        if event == "PAY_CANCEL":
            if order["status"] == "PAID":
                return {"status": "REJECTED_CONFLICT", "reason": "order_paid"}
            order["status"] = "CANCELLED"
            self.processed_callbacks.add(callback_id)
            return {"status": "CANCELLED", "order_id": order_id}

        return {"status": "UNSUPPORTED_EVENT", "event": event}

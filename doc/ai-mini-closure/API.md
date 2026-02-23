# API / Contract Notes

Date: 2026-02-23

## B-3 Simulation Contract
Module:
- `/Users/xa/Desktop/简历/resume-backend/examples/payment_idempotency.py`

Class:
- `PaymentStore`

Methods:
1. `create_order(order_id: str, amount_cents: int) -> dict`
2. `handle_callback(order_id, callback_id, event, paid_amount_cents) -> dict`

Events:
1. `PAY_SUCCESS`
2. `PAY_CANCEL`

Result statuses (subset):
1. `PAID`
2. `CANCELLED`
3. `IGNORED_DUPLICATE`
4. `REJECTED_AMOUNT_MISMATCH`
5. `REJECTED_CONFLICT`

## G-1 Workflow Contract
Repository closure is considered complete only when these files exist:
1. `PLAN.md`
2. `WORKLOG.md`
3. `CODE-REVIEW.md`
4. `API.md`
5. `TEST-REPORT.md`

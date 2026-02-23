from examples.payment_idempotency import PaymentStore


def test_success_callback_is_idempotent_by_callback_id():
    store = PaymentStore()
    store.create_order("ord-100", 9900)

    first = store.handle_callback(
        order_id="ord-100",
        callback_id="cb-1",
        event="PAY_SUCCESS",
        paid_amount_cents=9900,
    )
    second = store.handle_callback(
        order_id="ord-100",
        callback_id="cb-1",
        event="PAY_SUCCESS",
        paid_amount_cents=9900,
    )

    assert first["status"] == "PAID"
    assert second["status"] == "IGNORED_DUPLICATE"
    assert store.orders["ord-100"]["status"] == "PAID"


def test_mismatch_amount_is_rejected_and_state_kept():
    store = PaymentStore()
    store.create_order("ord-101", 5000)

    result = store.handle_callback(
        order_id="ord-101",
        callback_id="cb-2",
        event="PAY_SUCCESS",
        paid_amount_cents=4900,
    )

    assert result["status"] == "REJECTED_AMOUNT_MISMATCH"
    assert store.orders["ord-101"]["status"] == "PENDING"


def test_paid_order_rejects_cancel_transition():
    store = PaymentStore()
    store.create_order("ord-102", 7600)
    store.handle_callback(
        order_id="ord-102",
        callback_id="cb-3",
        event="PAY_SUCCESS",
        paid_amount_cents=7600,
    )

    result = store.handle_callback(
        order_id="ord-102",
        callback_id="cb-4",
        event="PAY_CANCEL",
        paid_amount_cents=7600,
    )

    assert result["status"] == "REJECTED_CONFLICT"
    assert store.orders["ord-102"]["status"] == "PAID"

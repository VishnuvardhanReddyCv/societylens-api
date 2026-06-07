# TODO Phase 2: Razorpay payment integration.
# All Razorpay webhook handlers and payment logic should import from this module.
# Keep all financial calculations here so the /api/admin/summary endpoint
# can be extended with payment data without touching routers.


async def calculate_maintenance_dues(complex_id: str, month: str) -> dict:
    """Stub: will calculate per-unit dues based on the expense pool."""
    return {}


async def process_payment_webhook(payload: dict) -> None:
    """Stub: will handle Razorpay webhook events (payment.captured, etc.)."""
    pass


async def get_collected_amount(complex_id: str) -> float:
    """Stub: will sum confirmed Razorpay payments for the complex."""
    return 0.0

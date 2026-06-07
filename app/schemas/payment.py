from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.payment import PaymentStatus


class PaymentCreate(BaseModel):
    amount: Decimal
    description: str
    user_id: str | None = None  # admin supplies this to record on behalf of a tenant


class PaymentOut(BaseModel):
    id: str
    complex_id: str
    user_id: str
    amount: Decimal
    description: str
    status: PaymentStatus
    recorded_by: str
    approved_by: str | None
    created_at: datetime
    approved_at: datetime | None
    payer_name: str | None = None
    payer_unit: str | None = None

    model_config = {"from_attributes": True}


class TenantPaymentSummary(BaseModel):
    user_id: str
    name: str
    email: str
    unit_number: str | None
    total_paid: float
    payment_count: int
    last_payment_at: datetime | None

from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from src.schemas.recurring import (
    RecurringPaymentCreate,
    RecurringPaymentResponse,
    RecurringPaymentUpdate,
)

recurring_router = APIRouter(prefix="/recurring-payments", tags=["recurring-payments"])
RECURRING_PAYMENTS: dict[int, RecurringPaymentResponse] = {}
_next_recurring_id = 1


@recurring_router.post("/", response_model=RecurringPaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_recurring_payment(payload: RecurringPaymentCreate) -> RecurringPaymentResponse:
    global _next_recurring_id

    item = RecurringPaymentResponse(
        id=_next_recurring_id,
        name=payload.name,
        amount=payload.amount,
        category=payload.category,
        frequency=payload.frequency,
        next_due_date=payload.next_due_date,
        created_at=datetime.utcnow(),
    )
    RECURRING_PAYMENTS[item.id] = item
    _next_recurring_id += 1
    return item


@recurring_router.get("/", response_model=list[RecurringPaymentResponse])
async def list_recurring_payments() -> list[RecurringPaymentResponse]:
    return sorted(RECURRING_PAYMENTS.values(), key=lambda item: item.next_due_date)


@recurring_router.get("/upcoming", response_model=list[RecurringPaymentResponse])
async def upcoming_recurring_payments() -> list[RecurringPaymentResponse]:
    upcoming = sorted(RECURRING_PAYMENTS.values(), key=lambda item: item.next_due_date)
    return upcoming


@recurring_router.get("/{recurring_id}", response_model=RecurringPaymentResponse)
async def get_recurring_payment(recurring_id: int) -> RecurringPaymentResponse:
    item = RECURRING_PAYMENTS.get(recurring_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurring payment not found")
    return item


@recurring_router.patch("/{recurring_id}", response_model=RecurringPaymentResponse)
async def update_recurring_payment(recurring_id: int, payload: RecurringPaymentUpdate) -> RecurringPaymentResponse:
    item = RECURRING_PAYMENTS.get(recurring_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurring payment not found")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return item
    for field, value in updates.items():
        setattr(item, field, value)
    RECURRING_PAYMENTS[recurring_id] = item
    return item


@recurring_router.delete("/{recurring_id}")
async def delete_recurring_payment(recurring_id: int) -> dict[str, str]:
    if recurring_id not in RECURRING_PAYMENTS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurring payment not found")
    del RECURRING_PAYMENTS[recurring_id]
    return {"message": "Recurring payment deleted successfully"}

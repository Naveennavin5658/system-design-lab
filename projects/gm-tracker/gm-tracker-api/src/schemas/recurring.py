from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.transaction import TransactionCategory


class RecurringPaymentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=120)
    amount: Decimal = Field(..., gt=0)
    category: TransactionCategory
    frequency: str = Field(default="monthly", pattern=r"^(daily|weekly|monthly|yearly)$")
    next_due_date: date


class RecurringPaymentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=120)
    amount: Decimal | None = Field(default=None, gt=0)
    category: TransactionCategory | None = None
    frequency: str | None = Field(default=None, pattern=r"^(daily|weekly|monthly|yearly)$")
    next_due_date: date | None = None


class RecurringPaymentResponse(BaseModel):
    id: int
    name: str
    amount: Decimal
    category: TransactionCategory
    frequency: str
    next_due_date: date
    created_at: datetime

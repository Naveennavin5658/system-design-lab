from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class TransactionCategory(str, Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    RENT = "rent"
    SALARY = "salary"
    INSURANCE = "insurance"
    INVESTMENT = "investment"
    FAMILY = "family"
    OTHER = "other"


class TransactionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Decimal = Field(..., gt=0)
    type: TransactionType
    category: TransactionCategory
    description: str | None = Field(default=None, max_length=255)
    transaction_date: date


class TransactionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Decimal | None = Field(default=None, gt=0)
    type: TransactionType | None = None
    category: TransactionCategory | None = None
    description: str | None = Field(default=None, max_length=255)
    transaction_date: date | None = None


class TransactionResponse(BaseModel):
    id: int
    amount: Decimal
    type: TransactionType
    category: TransactionCategory
    description: str | None = None
    transaction_date: date
    created_at: datetime


class TransactionFilter(BaseModel):
    type: TransactionType | None = None
    category: TransactionCategory | None = None
    from_date: date | None = None
    to_date: date | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

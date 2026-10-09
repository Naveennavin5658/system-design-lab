from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class GoalCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    target_date: date


class GoalUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    target_date: date | None = None


class GoalResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    target_date: date
    created_at: datetime
    updated_at: datetime


class GoalProgressCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Decimal = Field(..., gt=0)
    note: str | None = Field(default=None, max_length=255)


class GoalProgressResponse(BaseModel):
    id: int
    goal_id: int
    amount: Decimal
    note: str | None = None
    created_at: datetime

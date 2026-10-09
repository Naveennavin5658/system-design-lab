from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HabitCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    frequency: str = Field(default="daily", pattern=r"^(daily|weekly|monthly)$")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Name cannot be empty or whitespace.")
        return cleaned


class HabitUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    frequency: str | None = Field(default=None, pattern=r"^(daily|weekly|monthly)$")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Name cannot be empty or whitespace.")
        return cleaned


class HabitResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime
    frequency: str


class HabitCompletionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: date


class HabitCompletionResponse(BaseModel):
    habit_id: int
    date: date
    completed: bool = True


class HabitHistoryEntry(BaseModel):
    date: date
    completed: bool


class HabitHistoryResponse(BaseModel):
    habit: str
    current_streak: int
    longest_streak: int
    completion_rate: float
    history: list[HabitHistoryEntry]

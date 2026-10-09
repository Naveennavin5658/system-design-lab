from datetime import date, datetime, timedelta

from fastapi import APIRouter, HTTPException, status

from src.schemas.habit import (
    HabitCompletionCreate,
    HabitCompletionResponse,
    HabitCreate,
    HabitHistoryResponse,
    HabitResponse,
    HabitUpdate,
)

habits_router = APIRouter(prefix="/habits", tags=["habits"])
HABITS: dict[int, HabitResponse] = {}
HABIT_COMPLETIONS: dict[int, set[str]] = {}
_next_habit_id = 1


@habits_router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(payload: HabitCreate) -> HabitResponse:
    global _next_habit_id

    now = datetime.utcnow()
    habit = HabitResponse(
        id=_next_habit_id,
        name=payload.name,
        description=payload.description,
        created_at=now,
        updated_at=now,
        frequency=payload.frequency,
    )
    HABITS[habit.id] = habit
    HABIT_COMPLETIONS[habit.id] = set()
    _next_habit_id += 1
    return habit


@habits_router.get("/", response_model=list[HabitResponse])
async def list_habits() -> list[HabitResponse]:
    return [HABITS[habit_id] for habit_id in sorted(HABITS)]


@habits_router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(habit_id: int) -> HabitResponse:
    habit = HABITS.get(habit_id)
    if habit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    return habit


@habits_router.patch("/{habit_id}", response_model=HabitResponse)
async def update_habit(habit_id: int, payload: HabitUpdate) -> HabitResponse:
    habit = HABITS.get(habit_id)
    if habit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return habit
    for field, value in updates.items():
        if value is None:
            continue
        if field == "name":
            value = value.strip()
        setattr(habit, field, value)
    habit.updated_at = datetime.utcnow()
    HABITS[habit_id] = habit
    return habit


@habits_router.delete("/{habit_id}")
async def delete_habit(habit_id: int) -> dict[str, str]:
    if habit_id not in HABITS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    del HABITS[habit_id]
    HABIT_COMPLETIONS.pop(habit_id, None)
    return {"message": "Habit deleted successfully"}


@habits_router.post("/{habit_id}/completions", response_model=HabitCompletionResponse)
async def mark_habit_complete(habit_id: int, payload: HabitCompletionCreate) -> HabitCompletionResponse:
    if habit_id not in HABITS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    HABIT_COMPLETIONS.setdefault(habit_id, set()).add(payload.date.isoformat())
    return HabitCompletionResponse(habit_id=habit_id, date=payload.date, completed=True)


@habits_router.get("/{habit_id}/history", response_model=HabitHistoryResponse)
async def get_habit_history(habit_id: int) -> HabitHistoryResponse:
    habit = HABITS.get(habit_id)
    if habit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")

    completion_dates = {date.fromisoformat(value) for value in HABIT_COMPLETIONS.get(habit_id, set())}
    today = date.today()
    history = [
        {"date": today - timedelta(days=offset), "completed": (today - timedelta(days=offset)) in completion_dates}
        for offset in range(30)
    ]
    history.reverse()

    current_streak = 0
    cursor = today
    while cursor in completion_dates:
        current_streak += 1
        cursor -= timedelta(days=1)

    longest_streak = 0
    current_run = 0
    previous = None
    for day in sorted(completion_dates):
        if previous is not None and (day - previous).days == 1:
            current_run += 1
        else:
            current_run = 1
        longest_streak = max(longest_streak, current_run)
        previous = day

    completion_rate = round((sum(1 for item in history if item["completed"]) / len(history)) * 100, 1) if history else 0.0
    return HabitHistoryResponse(
        habit=habit.name,
        current_streak=current_streak,
        longest_streak=longest_streak,
        completion_rate=completion_rate,
        history=[{"date": item["date"], "completed": item["completed"]} for item in history],
    )

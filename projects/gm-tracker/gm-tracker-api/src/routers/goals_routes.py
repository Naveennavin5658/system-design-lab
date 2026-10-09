from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from src.schemas.goal import (
    GoalCreate,
    GoalProgressCreate,
    GoalProgressResponse,
    GoalResponse,
    GoalUpdate,
)

goals_router = APIRouter(prefix="/goals", tags=["goals"])
GOALS: dict[int, GoalResponse] = {}
GOAL_PROGRESS: dict[int, list[GoalProgressResponse]] = {}
_next_goal_id = 1
_next_progress_id = 1


@goals_router.post("/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(payload: GoalCreate) -> GoalResponse:
    global _next_goal_id

    goal = GoalResponse(
        id=_next_goal_id,
        title=payload.title,
        description=payload.description,
        target_date=payload.target_date,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    GOALS[goal.id] = goal
    GOAL_PROGRESS[goal.id] = []
    _next_goal_id += 1
    return goal


@goals_router.get("/", response_model=list[GoalResponse])
async def list_goals() -> list[GoalResponse]:
    return sorted(GOALS.values(), key=lambda item: item.target_date)


@goals_router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(goal_id: int) -> GoalResponse:
    goal = GOALS.get(goal_id)
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return goal


@goals_router.patch("/{goal_id}", response_model=GoalResponse)
async def update_goal(goal_id: int, payload: GoalUpdate) -> GoalResponse:
    goal = GOALS.get(goal_id)
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return goal
    for field, value in updates.items():
        setattr(goal, field, value)
    goal.updated_at = datetime.utcnow()
    GOALS[goal_id] = goal
    return goal


@goals_router.delete("/{goal_id}")
async def delete_goal(goal_id: int) -> dict[str, str]:
    if goal_id not in GOALS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    del GOALS[goal_id]
    GOAL_PROGRESS.pop(goal_id, None)
    return {"message": "Goal deleted successfully"}


@goals_router.post("/{goal_id}/progress", response_model=GoalProgressResponse, status_code=status.HTTP_201_CREATED)
async def add_goal_progress(goal_id: int, payload: GoalProgressCreate) -> GoalProgressResponse:
    if goal_id not in GOALS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    global _next_progress_id

    entry = GoalProgressResponse(
        id=_next_progress_id,
        goal_id=goal_id,
        amount=payload.amount,
        note=payload.note,
        created_at=datetime.utcnow(),
    )
    GOAL_PROGRESS.setdefault(goal_id, []).append(entry)
    _next_progress_id += 1
    return entry


@goals_router.get("/{goal_id}/progress", response_model=list[GoalProgressResponse])
async def list_goal_progress(goal_id: int) -> list[GoalProgressResponse]:
    if goal_id not in GOALS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return GOAL_PROGRESS.get(goal_id, [])

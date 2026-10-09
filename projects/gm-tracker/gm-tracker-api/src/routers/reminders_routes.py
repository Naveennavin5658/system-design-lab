from fastapi import APIRouter

reminders_router = APIRouter(prefix="/reminders", tags=["reminders"])


@reminders_router.get("/", response_model=list[dict])
async def list_reminders() -> list[dict]:
    return []

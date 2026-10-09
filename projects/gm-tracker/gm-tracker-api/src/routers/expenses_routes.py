from fastapi import APIRouter

expenses_router = APIRouter(prefix="/expenses", tags=["expenses"])


@expenses_router.get("/", response_model=list[dict])
async def list_expenses() -> list[dict]:
    return []

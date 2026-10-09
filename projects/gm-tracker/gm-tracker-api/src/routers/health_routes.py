from fastapi import APIRouter

health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("/", response_model=dict)
async def health_check() -> dict:
    return {"status": "ok"}

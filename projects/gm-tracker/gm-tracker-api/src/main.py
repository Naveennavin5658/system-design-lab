from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers.auth import auth_router
from src.routers.dashboard_routes import dashboard_router
from src.routers.expenses_routes import expenses_router
from src.routers.goals_routes import goals_router
from src.routers.habits_routes import habits_router
from src.routers.health_routes import health_router
from src.routers.recurring_routes import recurring_router
from src.routers.reminders_routes import reminders_router
from src.routers.transactions_routes import transactions_router

app = FastAPI(title="gm-tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://0.0.0.0:5173",
        "http://0.0.0.0:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (
    health_router,
    auth_router,
    transactions_router,
    recurring_router,
    goals_router,
    habits_router,
    expenses_router,
    reminders_router,
    dashboard_router,
):
    app.include_router(router)


@app.get("/", include_in_schema=False)
async def root() -> dict:
    return {"message": "gm-tracker-api"}

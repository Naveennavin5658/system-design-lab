from datetime import date, timedelta

from fastapi import APIRouter, Query

from src.routers.goals_routes import GOALS
from src.routers.habits_routes import HABITS, HABIT_COMPLETIONS
from src.routers.recurring_routes import RECURRING_PAYMENTS
from src.routers.transactions_routes import TRANSACTIONS
from src.schemas.dashboard import CategorySummary, DashboardResponse, FinanceSummary, GoalSummary, HabitSummary, MonthlyFinanceResponse, UpcomingPayment

dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@dashboard_router.get("/today", response_model=DashboardResponse)
async def dashboard_today() -> DashboardResponse:
    today = date.today()
    habits_total = len(HABITS)
    habits_completed = sum(1 for habit_id in HABIT_COMPLETIONS if today.isoformat() in HABIT_COMPLETIONS[habit_id])
    finance_income = sum(float(tx.amount) for tx in TRANSACTIONS.values() if tx.type.value == "income" and tx.transaction_date == today)
    finance_expenses = sum(float(tx.amount) for tx in TRANSACTIONS.values() if tx.type.value == "expense" and tx.transaction_date == today)
    due_soon = sum(1 for goal in GOALS.values() if goal.target_date <= today + timedelta(days=7))
    payments = [
        UpcomingPayment(
            name=item.name,
            amount=float(item.amount),
            due_date=item.next_due_date,
        )
        for item in RECURRING_PAYMENTS.values()
        if item.next_due_date <= today + timedelta(days=30)
    ]
    return DashboardResponse(
        date=today,
        habits=HabitSummary(
            total=habits_total,
            completed=habits_completed,
            completion_rate=round((habits_completed / habits_total * 100), 1) if habits_total else 0.0,
        ),
        finance=FinanceSummary(income=finance_income, expenses=finance_expenses),
        goals=GoalSummary(active=len(GOALS), due_soon=due_soon),
        upcoming_payments=payments,
    )


@dashboard_router.get("/finance", response_model=MonthlyFinanceResponse)
async def monthly_finance(year: int | None = Query(default=None), month: int | None = Query(default=None)) -> MonthlyFinanceResponse:
    today = date.today()
    selected_year = year or today.year
    selected_month = month or today.month
    month_items = [
        tx for tx in TRANSACTIONS.values() if tx.transaction_date.year == selected_year and tx.transaction_date.month == selected_month
    ]
    total_income = sum(float(tx.amount) for tx in month_items if tx.type.value == "income")
    total_expenses = sum(float(tx.amount) for tx in month_items if tx.type.value == "expense")
    total_investments = sum(float(tx.amount) for tx in month_items if tx.category.value == "investment")
    categories: dict[str, float] = {}
    for tx in month_items:
        categories[tx.category.value] = categories.get(tx.category.value, 0.0) + float(tx.amount)

    return MonthlyFinanceResponse(
        year=selected_year,
        month=selected_month,
        total_income=total_income,
        total_expenses=total_expenses,
        total_investments=total_investments,
        remaining=total_income - total_expenses - total_investments,
        categories=[CategorySummary(category=name, amount=amount) for name, amount in sorted(categories.items())],
    )

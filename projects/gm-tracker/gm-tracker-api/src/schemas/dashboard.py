from datetime import date

from pydantic import BaseModel


class HabitSummary(BaseModel):
    total: int
    completed: int
    completion_rate: float


class FinanceSummary(BaseModel):
    income: float
    expenses: float


class GoalSummary(BaseModel):
    active: int
    due_soon: int


class UpcomingPayment(BaseModel):
    name: str
    amount: float
    due_date: date


class DashboardResponse(BaseModel):
    date: date
    habits: HabitSummary
    finance: FinanceSummary
    goals: GoalSummary
    upcoming_payments: list[UpcomingPayment]


class CategorySummary(BaseModel):
    category: str
    amount: float


class MonthlyFinanceResponse(BaseModel):
    year: int
    month: int
    total_income: float
    total_expenses: float
    total_investments: float
    remaining: float
    categories: list[CategorySummary]

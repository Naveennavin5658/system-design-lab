from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.transaction import (
    TransactionCreate,
    TransactionFilter,
    TransactionResponse,
    TransactionType,
    TransactionUpdate,
)

transactions_router = APIRouter(prefix="/transactions", tags=["transactions"])
TRANSACTIONS: dict[int, TransactionResponse] = {}
_next_transaction_id = 1


def _sort_transactions(items: list[TransactionResponse]) -> list[TransactionResponse]:
    return sorted(items, key=lambda item: item.transaction_date, reverse=True)


@transactions_router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(payload: TransactionCreate) -> TransactionResponse:
    global _next_transaction_id

    tx = TransactionResponse(
        id=_next_transaction_id,
        amount=payload.amount,
        type=payload.type,
        category=payload.category,
        description=payload.description,
        transaction_date=payload.transaction_date,
        created_at=datetime.utcnow(),
    )
    TRANSACTIONS[tx.id] = tx
    _next_transaction_id += 1
    return tx


@transactions_router.get("/", response_model=list[TransactionResponse])
async def list_transactions(filters: TransactionFilter = Depends()) -> list[TransactionResponse]:
    items = list(TRANSACTIONS.values())
    if filters.type is not None:
        items = [item for item in items if item.type == filters.type]
    if filters.category is not None:
        items = [item for item in items if item.category == filters.category]
    if filters.from_date is not None:
        items = [item for item in items if item.transaction_date >= filters.from_date]
    if filters.to_date is not None:
        items = [item for item in items if item.transaction_date <= filters.to_date]

    items = _sort_transactions(items)
    start = (filters.page - 1) * filters.page_size
    end = start + filters.page_size
    return items[start:end]


@transactions_router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int) -> TransactionResponse:
    tx = TRANSACTIONS.get(transaction_id)
    if tx is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return tx


@transactions_router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(transaction_id: int, payload: TransactionUpdate) -> TransactionResponse:
    tx = TRANSACTIONS.get(transaction_id)
    if tx is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return tx

    for field, value in updates.items():
        setattr(tx, field, value)
    TRANSACTIONS[transaction_id] = tx
    return tx


@transactions_router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int) -> dict[str, str]:
    if transaction_id not in TRANSACTIONS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    del TRANSACTIONS[transaction_id]
    return {"message": "Transaction deleted successfully"}

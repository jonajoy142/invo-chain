# app/schemas/transaction.py
from typing import Optional
from pydantic import BaseModel, condecimal
from datetime import datetime

class TransactionBase(BaseModel):
    amount: float
    transaction_type: str
    blockchain_tx_hash: str

class TransactionCreate(TransactionBase):
    invoice_id: int

class Transaction(TransactionBase):
    id: int
    invoice_id: int
    investor_id: str
    status: str
    block_number: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
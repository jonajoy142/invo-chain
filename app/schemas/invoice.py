from pydantic import BaseModel, condecimal
from typing import Optional
from datetime import datetime
from decimal import Decimal

class InvoiceBase(BaseModel):
    invoice_number: str
    amount: condecimal(max_digits=20, decimal_places=2)
    currency: str = "USD"
    due_date: datetime
    discount_rate: condecimal(max_digits=5, decimal_places=2)
    customer_name: str
    customer_email: str

class InvoiceCreate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    id: int
    seller_id: str
    status: str
    token_id: Optional[int] = None
    contract_address: Optional[str] = None
    available_amount: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

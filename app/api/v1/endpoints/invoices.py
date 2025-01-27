from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ....schemas.invoice import InvoiceCreate, Invoice
from ....dependencies import verify_token
from ....database import supabase

router = APIRouter()

@router.post("/", response_model=Invoice)
async def create_invoice(
    invoice: InvoiceCreate,
    user = Depends(verify_token)
):
    try:
        # Convert Decimal fields to float
        issue_date = datetime.utcnow().isoformat() 
        invoice_data = invoice.model_dump()
        invoice_data = {
            key: (
                float(value) if isinstance(value, Decimal) else
                value.isoformat() if isinstance(value, datetime) else
                value
            )
            for key, value in invoice_data.items()
        }

        # Create invoice in database
        response = supabase.table('invoices').insert({
            **invoice_data,
            'seller_id': user["sub"],
            'status': 'DRAFT',
            'available_amount': float(invoice.amount),
            'issue_date': issue_date
        }).execute()
        
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Invoice])
async def list_invoices(
    user = Depends(verify_token),
    status: str = None
):
    try:
        query = supabase.table('invoices').select('*')
        
        if status:
            query = query.eq('status', status)
            
        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{invoice_id}", response_model=Invoice)
async def get_invoice(
    invoice_id: int,
    user = Depends(verify_token)
):
    try:
        response = supabase.table('invoices').select('*').eq('id', invoice_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
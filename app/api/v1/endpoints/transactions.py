from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ....schemas.trasaction import TransactionCreate, Transaction
from ....dependencies import verify_token
from ....database import supabase
from decimal import Decimal

router = APIRouter()

@router.post("/", response_model=Transaction)
async def create_transaction(
    transaction: TransactionCreate,
    user=Depends(verify_token)
):
    try:
        # Verify the invoice exists and has sufficient available amount
        print(transaction.invoice_id, "isTrans")
        invoice_response = supabase.table('invoices').select('*').eq('id', transaction.invoice_id).execute()
        print("Raw Invoice Response:", invoice_response)

        if not invoice_response.data:  # Ensure data exists
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice = invoice_response.data[0]
        available_amount = Decimal(invoice['available_amount'])
        
        if available_amount < transaction.amount:
            raise HTTPException(status_code=400, detail="Insufficient available amount")
        
        # Create transaction record
        transaction_data = {
            **transaction.model_dump(),
            'investor_id': user["sub"],
            'status': 'PENDING',
            'block_number': "block_number"
        }
        
        transaction_response = supabase.table('transactions').insert(transaction_data).execute()

        # Update invoice available amount
        new_available_amount = available_amount - transaction.amount
        supabase.table('invoices').update({
            'available_amount': str(new_available_amount)  # Convert to string for serialization
        }).eq('id', transaction.invoice_id).execute()

        # Serialize Decimal fields in the response before returning
        transaction_record = transaction_response.data[0]
        transaction_record = {
            key: (str(value) if isinstance(value, Decimal) else value)
            for key, value in transaction_record.items()
        }

        return transaction_record
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/", response_model=List[Transaction])
async def list_transactions(
    user = Depends(verify_token),
    invoice_id: int = None
):
    try:
        query = supabase.table('transactions').select('*')
        
        # Filter by user's transactions (either as investor or invoice seller)
        query = query.or_(
            f'investor_id.eq.{user.id},invoice.seller_id.eq.{user.id}'
        )
        
        if invoice_id:
            query = query.eq('invoice_id', invoice_id)
            
        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{transaction_id}", response_model=Transaction)
async def get_transaction(
    transaction_id: int,
    user = Depends(verify_token)
):
    try:
        response = supabase.table('transactions').select('*').eq('id', transaction_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Transaction not found")
            
        transaction = response.data[0]
        
        # Check if user has permission to view this transaction
        invoice_response = supabase.table('invoices').select('seller_id').eq('id', transaction['invoice_id']).execute()
        if not invoice_response.data:
            raise HTTPException(status_code=404, detail="Invoice not found")
            
        if (transaction['investor_id'] != user.id and 
            invoice_response.data[0]['seller_id'] != user.id):
            raise HTTPException(status_code=403, detail="Not authorized to view this transaction")
            
        return transaction
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{transaction_id}/status", response_model=Transaction)
async def update_transaction_status(
    transaction_id: int,
    status: str,
    user = Depends(verify_token)
):
    try:
        # Verify transaction exists and user has permission
        transaction_response = supabase.table('transactions').select('*').eq('id', transaction_id).execute()
        if not transaction_response.data:
            raise HTTPException(status_code=404, detail="Transaction not found")
            
        transaction = transaction_response.data[0]
        
        # Only allow status updates by the investor
        if transaction['investor_id'] != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this transaction")
            
        # Update transaction status
        response = supabase.table('transactions').update({
            'status': status
        }).eq('id', transaction_id).execute()
        
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
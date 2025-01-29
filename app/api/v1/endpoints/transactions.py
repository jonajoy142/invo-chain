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
        invoice_response = supabase.table('invoices').select('*').eq('id', transaction.invoice_id).execute()
        if not invoice_response.data:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice = invoice_response.data[0]
        available_amount = Decimal(str(invoice['available_amount']))
        transaction_amount = Decimal(str(transaction.amount))
        
        if available_amount < transaction_amount:
            raise HTTPException(status_code=400, detail="Insufficient available amount")
        
        transaction_data = {
            'amount': str(transaction_amount),
            'transaction_type': transaction.transaction_type,
            'blockchain_tx_hash': transaction.blockchain_tx_hash,
            'invoice_id': transaction.invoice_id,
            'investor_id': user["sub"],
            'status': 'PENDING',
            'block_number': None
        }
        
        transaction_response = supabase.table('transactions').insert(transaction_data).execute()
        
        new_available_amount = available_amount - transaction_amount
        supabase.table('invoices').update({
            'available_amount': str(new_available_amount)
        }).eq('id', transaction.invoice_id).execute()

        return transaction_response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/", response_model=List[Transaction])
async def list_transactions(
    user = Depends(verify_token),
    invoice_id: int = None
):
    try:
        query = supabase.table('transactions').select('*, invoices(seller_id)')
        
        # Filter by user's transactions (either as investor or invoice seller)
        query = query.or_(
            f"investor_id.eq.{user['sub']}",
            f"invoices.seller_id.eq.{user['sub']}"
        )
        
        if invoice_id:
            query = query.eq('invoice_id', invoice_id)
            
        response = query.execute()
        return [item['transactions'] for item in response.data]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{transaction_id}", response_model=Transaction)
async def get_transaction(
    transaction_id: int,
    user = Depends(verify_token)
):
    try:
        response = supabase.table('transactions').select('*').eq('id', transaction_id).execute()
        print(response, "res", transaction_id, "transaction_id")
        if not response.data:
            raise HTTPException(status_code=404, detail="Transaction not found")
        print(user, "USER12")
        transaction = response.data[0]
        
        # Check if user has permission to view this transaction
        invoice_response = supabase.table('invoices').select('seller_id').eq('id', transaction['invoice_id']).execute()
        if not invoice_response.data:
            raise HTTPException(status_code=404, detail="Invoice not found")
            
        if (transaction['investor_id'] != user["sub"] and 
            invoice_response.data[0]['seller_id'] != user["sub"]):
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
        # First verify the transaction exists - removed .single()
        transaction_response = supabase.table('transactions').select('*').eq('id', transaction_id).execute()
        
        if not transaction_response.data:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        transaction = transaction_response.data[0]
        
        # Verify user permission
        if transaction['investor_id'] != user["sub"]:
            raise HTTPException(status_code=403, detail="Not authorized to update this transaction")
        
        # Validate status value
        valid_statuses = ['PENDING', 'COMPLETED', 'CANCELLED', 'FAILED']
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        # Check if status is already set
        if transaction['status'] == status:
            raise HTTPException(status_code=400, detail="Status is already set to the same value")
        
        # Update the status
        update_response = supabase.table('transactions')\
            .update({'status': status})\
            .eq('id', transaction_id)\
            .eq('investor_id', user["sub"])\
            .execute()
            
        if not update_response.data:
            raise HTTPException(status_code=400, detail="Failed to update transaction status")
        
        return update_response.data[0]
        
    except Exception as e:
        if "Invalid input syntax for type" in str(e):
            raise HTTPException(status_code=400, detail="Invalid transaction ID format")
        raise HTTPException(status_code=400, detail=str(e))
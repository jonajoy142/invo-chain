from fastapi import APIRouter
from .endpoints import users, invoices, transactions, auth

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
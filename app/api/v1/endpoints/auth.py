# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, HTTPException, Depends
from ....schemas.user import UserCreate, User
from ....dependencies import verify_token
from ....database import supabase

router = APIRouter()

@router.post("/signup", response_model=User)
async def signup(user: UserCreate,):
    try:
        auth_response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password
        })
        
        # Profile is created automatically via trigger
        print(auth_response, "AUTH RESPONSE TEST")
        new_user = auth_response.user
        user_response = User(
            id=new_user.id,  # Adjust with the actual fields in `auth_response.user`
            email=new_user.email,
            wallet_address=user.wallet_address,
            user_type=user.user_type,
            business_name=user.business_name if user.business_name else None,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at,
            kyc_status = "PENDING"
        )

        return user_response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(email: str, password: str):
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return auth_response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ....schemas.user import User, UserBase
from ....dependencies import verify_token
from ....database import supabase

router = APIRouter()

@router.get("/me", response_model=User)
async def get_current_user(
    user=Depends(verify_token)
):
    try:
        response = supabase.table('profiles').select('*').eq('id', user["sub"]).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/me", response_model=User)
async def update_user(
    user_update: UserBase,
    user = Depends(verify_token)
):
    try:
        response = supabase.table('profiles').update(
            user_update.model_dump(exclude_unset=True)
        ).eq('id', user["sub"]).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    user = Depends(verify_token)
):
    try:
        response = supabase.table('profiles').select('*').eq('id', user_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 
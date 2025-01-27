from fastapi import Header, HTTPException, Depends
from typing import Annotated
from .database import supabase
from .config import settings

async def verify_token(authorization: Annotated[str | None, Header()] = None):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        token = authorization.split(" ")[1]
        user_response = supabase.auth.get_user(token)
        
        # Debugging: Inspect the user_response and user_response.user
        print("User response:", user_response)
        print("Type of user_response:", type(user_response))
        
        # Adjust depending on the actual structure
        if not user_response or not hasattr(user_response, "user"):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Extract user ID (adjust based on actual structure)
        user_id = user_response.user.id  # Assuming `user_response.user` has an `id` attribute
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")
        
        return {"sub": user_id}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

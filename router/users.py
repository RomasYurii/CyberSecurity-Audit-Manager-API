from fastapi import APIRouter, Depends
from database import schemas, models
from security.security import get_current_user

router = APIRouter()

@router.get("/users/me", response_model=schemas.UserResponse)
async def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user
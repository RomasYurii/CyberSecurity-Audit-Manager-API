from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from database import models
from security.security import verify_password, create_access_token, limiter

router = APIRouter()

@router.post("/login")
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(models.User).filter(models.User.username == form_data.username)
    result = await db.execute(stmt)
    existing_user = result.scalars().first()

    if not existing_user or not verify_password(form_data.password, existing_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": existing_user.username})

    return {"access_token": access_token, "token_type": "bearer"}
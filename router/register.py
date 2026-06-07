from fastapi import APIRouter, HTTPException, status, Depends
from database import schemas
from database.database import get_db, AsyncSessionLocal
from database import models
from security.security import get_password_hash
from sqlalchemy.future import select


router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: schemas.UserCreate, db: AsyncSessionLocal = Depends(get_db)):
    stmt = select(models.User).filter(
        (models.User.username == user.username) | (models.User.email == user.email)
    )

    result = await db.execute(stmt)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "User created successfully", "username": new_user.username}
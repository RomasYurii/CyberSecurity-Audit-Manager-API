from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import models, schemas
from database.database import get_db
from security.security import get_current_user

router = APIRouter()

@router.post("/targets", status_code=status.HTTP_201_CREATED)
async def create_target(
    target: schemas.TargetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    stmt = select(models.Target).filter(
        (models.Target.ip_address == target.ip_address) | 
        (models.Target.domain == target.domain)
    )
    result = await db.execute(stmt)
    
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Target with this IP or domain already exists")

    new_target = models.Target(
        ip_address=target.ip_address,
        domain=target.domain,
        description=target.description,
        pentester_id=current_user.id
    )
    
    db.add(new_target)
    await db.commit()
    await db.refresh(new_target)
    
    return new_target
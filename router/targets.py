from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
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


@router.get("/targets", response_model=List[schemas.TargetResponse])
async def get_targets(
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    stmt = select(models.Target).filter(models.Target.pentester_id == current_user.id)
    result = await db.execute(stmt)

    return result.scalars().all()


@router.delete("/targets/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_target(
        target_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    stmt = select(models.Target).filter(
        models.Target.id == target_id,
        models.Target.pentester_id == current_user.id
    )
    result = await db.execute(stmt)
    target = result.scalars().first()

    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    await db.delete(target)
    await db.commit()

    return None
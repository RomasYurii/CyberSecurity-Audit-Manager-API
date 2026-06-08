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


@router.post("/targets/{target_id}/vulnerabilities", status_code=status.HTTP_201_CREATED)
async def add_vulnerability_to_target(
        target_id: int,
        data: schemas.TargetVulnerabilityCreate,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    stmt = select(models.Target).filter(
        models.Target.id == target_id,
        models.Target.pentester_id == current_user.id
    )
    target = (await db.execute(stmt)).scalars().first()

    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    target_vuln = models.TargetVulnerability(
        target_id=target_id,
        vulnerability_id=data.vulnerability_id,
        severity=data.severity
    )

    db.add(target_vuln)
    await db.commit()

    return {"message": "Vulnerability linked successfully"}


@router.get("/targets/{target_id}/vulnerabilities", response_model=List[schemas.TargetVulnerabilityResponse])
async def get_target_vulnerabilities(
        target_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    target_stmt = select(models.Target).filter(
        models.Target.id == target_id,
        models.Target.pentester_id == current_user.id
    )
    target = (await db.execute(target_stmt)).scalars().first()

    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    stmt = select(models.TargetVulnerability).filter(
        models.TargetVulnerability.target_id == target_id
    )
    result = await db.execute(stmt)

    return result.scalars().all()


@router.delete("/targets/{target_id}/vulnerabilities/{vulnerability_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_vulnerability_from_target(
        target_id: int,
        vulnerability_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    target_stmt = select(models.Target).filter(
        models.Target.id == target_id,
        models.Target.pentester_id == current_user.id
    )
    target = (await db.execute(target_stmt)).scalars().first()

    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    stmt = select(models.TargetVulnerability).filter(
        models.TargetVulnerability.target_id == target_id,
        models.TargetVulnerability.vulnerability_id == vulnerability_id
    )
    link = (await db.execute(stmt)).scalars().first()

    if not link:
        raise HTTPException(status_code=404, detail="Vulnerability link not found")

    await db.delete(link)
    await db.commit()

    return None
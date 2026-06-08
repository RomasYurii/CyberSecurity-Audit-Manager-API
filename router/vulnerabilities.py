from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database import models, schemas
from database.database import get_db

router = APIRouter()

@router.post("/vulnerabilities", status_code=status.HTTP_201_CREATED, response_model=schemas.VulnerabilityResponse)
async def create_vulnerability(
    vuln: schemas.VulnerabilityCreate,
    db: AsyncSession = Depends(get_db)
):
    new_vuln = models.Vulnerability(**vuln.model_dump())
    db.add(new_vuln)
    await db.commit()
    await db.refresh(new_vuln)
    return new_vuln

@router.get("/vulnerabilities", response_model=List[schemas.VulnerabilityResponse])
async def get_vulnerabilities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Vulnerability))
    return result.scalars().all()


@router.get("/vulnerabilities/{vulnerability_id}", response_model=schemas.VulnerabilityResponse)
async def get_vulnerability(vulnerability_id: int, db: AsyncSession = Depends(get_db)):
    vuln = (await db.execute(
        select(models.Vulnerability).filter(models.Vulnerability.id == vulnerability_id))).scalars().first()
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    return vuln


@router.patch("/vulnerabilities/{vulnerability_id}", response_model=schemas.VulnerabilityResponse)
async def update_vulnerability(
        vulnerability_id: int,
        vuln_update: schemas.VulnerabilityUpdate,
        db: AsyncSession = Depends(get_db)
):
    vuln = (await db.execute(
        select(models.Vulnerability).filter(models.Vulnerability.id == vulnerability_id))).scalars().first()
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")

    update_data = vuln_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(vuln, key, value)

    await db.commit()
    await db.refresh(vuln)
    return vuln


@router.delete("/vulnerabilities/{vulnerability_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vulnerability(vulnerability_id: int, db: AsyncSession = Depends(get_db)):
    vuln = (await db.execute(
        select(models.Vulnerability).filter(models.Vulnerability.id == vulnerability_id))).scalars().first()
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")

    await db.delete(vuln)
    await db.commit()
    return None
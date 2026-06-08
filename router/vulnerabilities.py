from fastapi import APIRouter, Depends, status
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
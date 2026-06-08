from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select

from database import models
from database.database import get_db
from security.security import get_current_user

router = APIRouter()


@router.get("/statistics")
async def get_statistics(
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    targets_count = await db.scalar(
        select(func.count(models.Target.id))
        .filter(models.Target.pentester_id == current_user.id)
    )

    vulns_count = await db.scalar(
        select(func.count(models.TargetVulnerability.target_id))
        .join(models.Target, models.Target.id == models.TargetVulnerability.target_id)
        .filter(models.Target.pentester_id == current_user.id)
    )

    return {
        "total_targets": targets_count,
        "total_vulnerabilities_found": vulns_count
    }
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from database import models, schemas
from database.database import get_db
from security.security import get_current_user
from typing import Optional, List
from fastapi import BackgroundTasks
from fastapi.responses import Response
import asyncio
from fastapi import Request
from limiter import limiter
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


@router.patch("/targets/{target_id}", response_model=schemas.TargetResponse)
async def update_target(
        target_id: int,
        target_update: schemas.TargetUpdate,
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

    # Оновлюємо лише передані поля
    update_data = target_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(target, key, value)

    await db.commit()
    await db.refresh(target)

    return target

@router.get("/targets/{target_id}", response_model=schemas.TargetResponse)
async def get_target(
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

    return target


@router.patch("/targets/{target_id}/vulnerabilities/{vulnerability_id}",
              response_model=schemas.TargetVulnerabilityResponse)
async def update_target_vulnerability_severity(
        target_id: int,
        vulnerability_id: int,
        data: schemas.TargetVulnerabilityUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    target = (await db.execute(select(models.Target).filter(models.Target.id == target_id,
                                                            models.Target.pentester_id == current_user.id))).scalars().first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    link = (await db.execute(select(models.TargetVulnerability).filter(
        models.TargetVulnerability.target_id == target_id,
        models.TargetVulnerability.vulnerability_id == vulnerability_id
    ))).scalars().first()

    if not link:
        raise HTTPException(status_code=404, detail="Vulnerability link not found")

    link.severity = data.severity
    await db.commit()
    await db.refresh(link)
    return link


@router.get("/targets/{target_id}/report", response_model=schemas.TargetReportResponse)
async def get_target_report(
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

    stmt = select(
        models.Vulnerability.id.label("vulnerability_id"),
        models.Vulnerability.name_en,
        models.TargetVulnerability.severity
    ).join(
        models.TargetVulnerability, models.Vulnerability.id == models.TargetVulnerability.vulnerability_id
    ).filter(
        models.TargetVulnerability.target_id == target_id
    )

    vulns = (await db.execute(stmt)).mappings().all()

    report_data = schemas.TargetResponse.model_validate(target).model_dump()
    report_data["vulnerabilities"] = vulns

    return report_data


@router.get("/targets", response_model=List[schemas.TargetResponse])
async def get_targets(
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    stmt = select(models.Target).filter(models.Target.pentester_id == current_user.id)

    # Пошук по частині домену
    if search:
        stmt = stmt.filter(models.Target.domain.ilike(f"%{search}%"))

    # Пагінація
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)

    return result.scalars().all()


async def mock_security_scan(target_id: int):
    # Імітація довгого процесу (наприклад, сканування Nmap)
    await asyncio.sleep(10)
    print(f"Scan finished for target ID: {target_id}")


@router.post("/targets/{target_id}/scan", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("3/minute")
async def start_target_scan(
        request: Request,
        target_id: int,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    target = (await db.execute(select(models.Target).filter(
        models.Target.id == target_id,
        models.Target.pentester_id == current_user.id
    ))).scalars().first()

    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    background_tasks.add_task(mock_security_scan, target_id)

    return {"message": "Security scan started in the background"}

@router.get("/targets/{target_id}/export")
async def export_target_csv(
    target_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    target = (await db.execute(select(models.Target).filter(
        models.Target.id == target_id,
        models.Target.pentester_id == current_user.id
    ))).scalars().first()

    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    stmt = select(models.Vulnerability.name_en, models.TargetVulnerability.severity).join(
        models.TargetVulnerability, models.Vulnerability.id == models.TargetVulnerability.vulnerability_id
    ).filter(models.TargetVulnerability.target_id == target_id)

    vulns = (await db.execute(stmt)).mappings().all()

    csv_data = "Vulnerability,Severity\n"
    for v in vulns:
        csv_data += f"{v['name_en']},{v['severity']}\n"

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=target_{target_id}_report.csv"}
    )
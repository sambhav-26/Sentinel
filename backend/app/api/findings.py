"""Finding management routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.models.database import get_db
from app.models import Finding
from app.schemas import FindingDetailResponse, FindingListResponse, FindingResponse
from datetime import datetime

router = APIRouter()


class IgnoreFindingRequest(BaseModel):
    """Request body for ignoring a finding."""
    ignore_reason: str = "User marked as false positive"


@router.get("", response_model=FindingListResponse)
async def list_findings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all findings with pagination."""
    # Get total count
    count_result = await db.execute(select(Finding))
    total = len(count_result.scalars().all())
    
    # Get paginated results
    query = select(Finding).offset(skip).limit(limit)
    result = await db.execute(query)
    findings = result.scalars().all()
    
    return FindingListResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=(total + limit - 1) // limit,
        items=[FindingResponse.from_orm(f) for f in findings]
    )


@router.get("/{finding_id}", response_model=FindingDetailResponse)
async def get_finding(
    finding_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get finding details."""
    finding = await db.get(Finding, finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    
    return FindingDetailResponse.from_orm(finding)


@router.post("/{finding_id}/ignore")
async def ignore_finding(
    finding_id: str,
    request: IgnoreFindingRequest,
    db: AsyncSession = Depends(get_db)
):
    """Mark finding as ignored (false positive)."""
    finding = await db.get(Finding, finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    
    finding.is_ignored = True
    finding.ignore_reason = request.ignore_reason
    finding.updated_at = datetime.now()
    
    await db.commit()
    await db.refresh(finding)
    
    return FindingResponse.from_orm(finding)

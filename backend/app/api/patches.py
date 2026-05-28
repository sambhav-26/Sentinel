"""Patch suggestion routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import get_db
from app.models import Patch
from app.schemas import PatchResponse, PatchListResponse

router = APIRouter()


@router.get("", response_model=PatchListResponse)
async def list_patches(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all patches with pagination."""
    # Get total count
    count_result = await db.execute(select(Patch))
    total = len(count_result.scalars().all())
    
    # Get paginated results
    query = select(Patch).offset(skip).limit(limit)
    result = await db.execute(query)
    patches = result.scalars().all()
    
    return PatchListResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=(total + limit - 1) // limit,
        items=[PatchResponse.from_orm(p) for p in patches]
    )


@router.get("/{patch_id}", response_model=PatchResponse)
async def get_patch(
    patch_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get patch details."""
    patch = await db.get(Patch, patch_id)
    if not patch:
        raise HTTPException(status_code=404, detail="Patch not found")
    
    return PatchResponse.from_orm(patch)

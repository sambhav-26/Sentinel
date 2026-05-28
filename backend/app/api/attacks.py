"""Attack simulation routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import get_db
from app.models import Attack
from app.schemas import AttackResponse, AttackListResponse

router = APIRouter()


@router.get("", response_model=AttackListResponse)
async def list_attacks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all attacks with pagination."""
    # Get total count
    count_result = await db.execute(select(Attack))
    total = len(count_result.scalars().all())
    
    # Get paginated results
    query = select(Attack).offset(skip).limit(limit)
    result = await db.execute(query)
    attacks = result.scalars().all()
    
    return AttackListResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=(total + limit - 1) // limit,
        items=[AttackResponse.from_orm(a) for a in attacks]
    )


@router.get("/{attack_id}", response_model=AttackResponse)
async def get_attack(
    attack_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get attack details."""
    attack = await db.get(Attack, attack_id)
    if not attack:
        raise HTTPException(status_code=404, detail="Attack not found")
    
    return AttackResponse.from_orm(attack)

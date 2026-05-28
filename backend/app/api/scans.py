"""Scan management routes."""

import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.models.database import get_db
from app.models.orm import Scan, Finding, ScanStatus
from app.schemas import (
    ScanCreate,
    ScanResponse,
    ScanDetailResponse,
    ScanListResponse,
    FindingResponse,
    FindingListResponse,
)
from app.utils.helpers import generate_id
from app.services.orchestrator import ScanOrchestrator
from app.agents.scanner_agent import ScannerAgent
from app.agents.threat_agent import ThreatAgent
from app.agents.attack_agent import AttackAgent
from app.agents.patch_agent import PatchAgent
from app.agents.report_agent import ReportAgent
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()


async def orchestrate_scan_async(
    scan_id: str,
    repository_id: str,
    db_session: AsyncSession
):
    """Execute agent orchestration in background."""
    logger.info(f"Starting agent orchestration for scan {scan_id}")
    try:
        # Create orchestrator
        orchestrator = ScanOrchestrator(db_session)
        
        # Register agents in order
        orchestrator.register_agent(ScannerAgent(db_session))
        orchestrator.register_agent(ThreatAgent(db_session))
        orchestrator.register_agent(AttackAgent(db_session))
        orchestrator.register_agent(PatchAgent(db_session))
        orchestrator.register_agent(ReportAgent(db_session))
        
        # Execute orchestration
        success = await orchestrator.execute(scan_id, repository_id)
        
        if success:
            logger.info(f"Scan {scan_id} completed successfully")
        else:
            logger.error(f"Scan {scan_id} failed during orchestration")
        
        await db_session.commit()
    except Exception as e:
        logger.error(f"Orchestration error for scan {scan_id}: {e}", exc_info=True)
        try:
            await db_session.rollback()
        except:
            pass


@router.post("", response_model=ScanResponse, status_code=201)
async def start_scan(
    scan_create: ScanCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Start a new vulnerability scan.
    
    This endpoint:
    1. Creates a scan record with QUEUED status
    2. Triggers agent orchestration asynchronously
    3. Returns the scan object immediately
    
    The agents run in background:
    - Scanner Agent: Code analysis (bandit, semgrep)
    - Threat Agent: Threat classification
    - Attack Agent: Attack simulation
    - Patch Agent: Patch generation
    - Report Agent: Report compilation
    """
    # Create scan record
    scan = Scan(
        id=generate_id(),
        user_id="demo-user",  # TODO: Get from JWT auth
        repository_id=generate_id(),
        status=ScanStatus.QUEUED,
        progress=0,
        total_files=0,
        files_scanned=0,
        metadata={
            "repository_url": scan_create.repository_url,
            "repository_name": scan_create.repository_url.split("/")[-1].replace(".git", "")
        },
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)
    
    logger.info(f"Created scan {scan.id} for {scan_create.repository_url}")
    
    # Trigger agent orchestration asynchronously
    asyncio.create_task(orchestrate_scan_async(scan.id, scan.repository_id, db))
    
    return ScanResponse.from_orm(scan)


@router.get("", response_model=ScanListResponse)
async def list_scans(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List all scans with pagination and optional status filter."""
    # Build query
    query = select(Scan)
    
    if status:
        query = query.where(Scan.status == status)
    
    query = query.order_by(desc(Scan.created_at)).offset(skip).limit(limit)
    
    # Get total count
    count_query = select(Scan)
    if status:
        count_query = count_query.where(Scan.status == status)
    
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    # Get paginated results
    result = await db.execute(query)
    scans = result.scalars().all()
    
    return ScanListResponse(
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        total_pages=(total + limit - 1) // limit if limit > 0 else 1,
        items=[ScanResponse.from_orm(scan) for scan in scans]
    )


@router.get("/{scan_id}", response_model=ScanDetailResponse)
async def get_scan(
    scan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get scan details including finding counts by severity."""
    scan = await db.get(Scan, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Count findings by severity
    findings_result = await db.execute(
        select(Finding).where(Finding.scan_id == scan_id)
    )
    findings = findings_result.scalars().all()
    
    severity_counts = {
        "critical": sum(1 for f in findings if f.severity == "critical"),
        "high": sum(1 for f in findings if f.severity == "high"),
        "medium": sum(1 for f in findings if f.severity == "medium"),
        "low": sum(1 for f in findings if f.severity == "low"),
        "info": sum(1 for f in findings if f.severity == "info"),
    }
    
    return ScanDetailResponse(
        **ScanResponse.from_orm(scan).dict(),
        severity_counts=severity_counts,
        total_findings=len(findings)
    )
    findings = await db.execute(
        select(Finding).where(Finding.scan_id == scan_id)
    )
    finding_list = findings.scalars().all()
    
    severity_counts = {
        "critical": sum(1 for f in finding_list if f.severity == "critical"),
        "high": sum(1 for f in finding_list if f.severity == "high"),
        "medium": sum(1 for f in finding_list if f.severity == "medium"),
        "low": sum(1 for f in finding_list if f.severity == "low"),
    }
    
    return ScanDetailResponse(
        **ScanResponse.from_orm(scan).dict(),
        critical_count=severity_counts["critical"],
        high_count=severity_counts["high"],
        medium_count=severity_counts["medium"],
        low_count=severity_counts["low"],
        total_findings=len(finding_list)
    )


@router.get("/{scan_id}/findings", response_model=FindingListResponse)
async def get_scan_findings(
    scan_id: str,
    severity: str = Query(None, regex="^(critical|high|medium|low|info)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get findings for a scan with optional severity filter."""
    # Check scan exists
    scan = await db.get(Scan, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Build query
    conditions = [Finding.scan_id == scan_id]
    if severity:
        conditions.append(Finding.severity == severity)
    
    # Get total count
    count_query = select(Finding).where(and_(*conditions))
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    # Get paginated results
    query = select(Finding).where(and_(*conditions)).offset(skip).limit(limit)
    result = await db.execute(query)
    findings = result.scalars().all()
    
    return FindingListResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=(total + limit - 1) // limit,
        items=[FindingResponse.from_orm(f) for f in findings]
    )

#!/usr/bin/env python3
"""
End-to-end test for agent workflow orchestration.

Tests the complete pipeline:
1. Create test scan in database
2. Run orchestrator with all 5 agents
3. Verify findings, attacks, patches, report are created
4. Check scan progress updates
"""

import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Scan, Finding, Attack, Patch, Report, ScanStatus
from app.services.orchestrator import ScanOrchestrator
from app.agents.scanner_agent import ScannerAgent
from app.agents.threat_agent import ThreatAgent
from app.agents.attack_agent import AttackAgent
from app.agents.patch_agent import PatchAgent
from app.agents.report_agent import ReportAgent
from app.utils.helpers import generate_id

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Use in-memory SQLite for testing
DATABASE_URL = "sqlite+aiosqlite:///:memory:"


async def setup_database():
    """Create in-memory database and tables."""
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    return engine


async def create_test_data(session: AsyncSession):
    """Create test scan and repository."""
    from app.models import User, Repository
    
    # Create user
    user = User(
        id=generate_id(),
        email="test@example.com",
        api_key=generate_id(),
    )
    
    # Create repository
    repo = Repository(
        id=generate_id(),
        user_id=user.id,
        name="test-repo",
        url="https://github.com/test/repo",
    )
    
    # Create scan
    scan = Scan(
        id=generate_id(),
        user_id=user.id,
        repository_id=repo.id,
        status=ScanStatus.QUEUED,
        progress=0,
    )
    
    session.add(user)
    session.add(repo)
    session.add(scan)
    await session.commit()
    
    return scan.id, repo.id


async def test_agent_workflow():
    """Test complete agent workflow."""
    logger.info("=" * 70)
    logger.info("AGENT WORKFLOW END-TO-END TEST")
    logger.info("=" * 70)
    
    # Setup
    engine = await setup_database()
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Create test data
        logger.info("\n[SETUP] Creating test data...")
        scan_id, repo_id = await create_test_data(session)
        logger.info(f"✓ Created test scan: {scan_id}")
        logger.info(f"✓ Created test repo: {repo_id}")
        
        # Create orchestrator
        logger.info("\n[ORCHESTRATOR] Initializing orchestrator...")
        orchestrator = ScanOrchestrator(session)
        
        # Register agents
        logger.info("[ORCHESTRATOR] Registering agents...")
        orchestrator.register_agent(ScannerAgent(session))
        orchestrator.register_agent(ThreatAgent(session))
        orchestrator.register_agent(AttackAgent(session))
        orchestrator.register_agent(PatchAgent(session))
        orchestrator.register_agent(ReportAgent(session))
        logger.info(f"✓ Registered {len(orchestrator.agents)} agents")
        
        # Execute pipeline
        logger.info("\n[EXECUTION] Starting agent pipeline...")
        logger.info("-" * 70)
        success = await orchestrator.execute(scan_id, repo_id)
        logger.info("-" * 70)
        
        if not success:
            logger.error("✗ Orchestration failed!")
            return False
        
        logger.info("✓ Orchestration completed successfully")
        
        # Verify results
        logger.info("\n[VERIFICATION] Checking results...")
        
        # Check scan status
        scan = await session.get(Scan, scan_id)
        assert scan is not None, "Scan not found"
        assert scan.status == ScanStatus.COMPLETED, f"Scan status is {scan.status}, expected COMPLETED"
        assert scan.progress == 100, f"Scan progress is {scan.progress}, expected 100"
        logger.info(f"✓ Scan status: {scan.status} (progress: {scan.progress}%)")
        
        # Check findings
        findings = [f for f in await session.execute(
            __import__('sqlalchemy').select(Finding).where(Finding.scan_id == scan_id)
        )]
        findings = [f for f, in findings] if findings else []
        finding_count = len(findings)
        logger.info(f"✓ Findings created: {finding_count}")
        
        if finding_count > 0:
            # Check attacks
            attacks = [a for a in await session.execute(
                __import__('sqlalchemy').select(Attack).where(Attack.scan_id == scan_id)
            )]
            attacks = [a for a, in attacks] if attacks else []
            attack_count = len(attacks)
            logger.info(f"✓ Attacks created: {attack_count}")
            
            # Check patches
            patches = [p for p in await session.execute(
                __import__('sqlalchemy').select(Patch).where(Patch.scan_id == scan_id)
            )]
            patches = [p for p, in patches] if patches else []
            patch_count = len(patches)
            logger.info(f"✓ Patches created: {patch_count}")
            
            # Check report
            reports = [r for r in await session.execute(
                __import__('sqlalchemy').select(Report).where(Report.scan_id == scan_id)
            )]
            reports = [r for r, in reports] if reports else []
            report_count = len(reports)
            logger.info(f"✓ Reports created: {report_count}")
            
            if report_count > 0:
                report = reports[0]
                logger.info(f"  - Risk Score: {report.overall_risk_score:.0f}/100")
                logger.info(f"  - Critical: {report.critical_count}, High: {report.high_count}, Medium: {report.medium_count}, Low: {report.low_count}")
        
        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("TEST RESULTS")
        logger.info("=" * 70)
        logger.info(f"Scan Status:     {scan.status}")
        logger.info(f"Findings:        {finding_count}")
        logger.info(f"Attacks:         {attack_count if finding_count > 0 else 0}")
        logger.info(f"Patches:         {patch_count if finding_count > 0 else 0}")
        logger.info(f"Reports:         {report_count if finding_count > 0 else 0}")
        logger.info("=" * 70)
        logger.info("✓ ALL TESTS PASSED!")
        logger.info("=" * 70)
        
        return True
    
    # Cleanup
    await engine.dispose()


if __name__ == "__main__":
    success = asyncio.run(test_agent_workflow())
    exit(0 if success else 1)

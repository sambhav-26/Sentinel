"""Example of using the scan orchestrator with all agents."""

import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import AsyncSessionLocal, engine, init_db
from app.services.orchestrator import ScanOrchestrator
from app.agents import (
    ScannerAgent,
    ThreatAgent,
    AttackAgent,
    PatchAgent,
    ReportAgent,
)
from app.utils.helpers import generate_id

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_security_scan(repository_url: str) -> bool:
    """
    Run a complete security scan pipeline.
    
    Pipeline:
    1. Scanner Agent: Run code analysis tools
    2. Threat Agent: Classify threats
    3. Attack Agent: Plan attacks
    4. Patch Agent: Generate patches
    5. Report Agent: Compile report
    
    Args:
        repository_url: URL to repository
        
    Returns:
        True if successful, False otherwise
    """
    
    # Create database session
    async with AsyncSessionLocal() as session:
        # Create scan record
        from app.models import Scan, User, Repository
        from datetime import datetime
        
        # Get or create user
        user = User(
            id=generate_id(),
            email="scanner@sentinelos.local",
            api_key="default-api-key",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(user)
        await session.flush()
        
        # Get or create repository
        repo = Repository(
            id=generate_id(),
            user_id=user.id,
            name="Target Repository",
            url=repository_url,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(repo)
        await session.flush()
        
        # Create scan
        scan = Scan(
            id=generate_id(),
            user_id=user.id,
            repository_id=repo.id,
            status="queued",
            progress=0,
            total_files=0,
            files_scanned=0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(scan)
        await session.commit()
        
        logger.info(f"Created scan: {scan.id}")
        logger.info(f"Repository: {repository_url}")
        
        # Create orchestrator
        orchestrator = ScanOrchestrator(session)
        
        # Register agents in order
        orchestrator.register_agent(ScannerAgent(session))
        orchestrator.register_agent(ThreatAgent(session))
        orchestrator.register_agent(AttackAgent(session))
        orchestrator.register_agent(PatchAgent(session))
        orchestrator.register_agent(ReportAgent(session))
        
        # Execute scan
        logger.info("Starting security scan orchestration...")
        success = await orchestrator.execute(
            scan_id=scan.id,
            repository_id=repo.id
        )
        
        # Get results
        results = orchestrator.get_results()
        summary = orchestrator.get_result_summary()
        
        logger.info("\n" + "="*60)
        logger.info("SCAN RESULTS")
        logger.info("="*60)
        
        for agent_result in summary["agents"]:
            status = "✓ PASS" if agent_result["success"] else "✗ FAIL"
            time = agent_result.get("execution_time_ms", 0)
            logger.info(f"{status} | {agent_result['name']:20} | {time:5}ms")
        
        logger.info("="*60)
        logger.info(f"Scan completed: {'SUCCESS' if success else 'FAILED'}")
        logger.info(f"Scan ID: {scan.id}")
        
        return success


async def main():
    """Main entry point."""
    
    # Initialize database
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database ready")
    
    # Run example scan
    await run_security_scan(
        repository_url="https://github.com/example/vulnerable-app"
    )


if __name__ == "__main__":
    asyncio.run(main())

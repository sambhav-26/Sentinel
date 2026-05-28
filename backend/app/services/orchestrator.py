"""Scan orchestration service for coordinating agents."""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Scan, ScanStatus, AgentLog
from app.agents.base import BaseAgent, AgentInput, AgentOutput
from app.utils.helpers import generate_id


logger = logging.getLogger(__name__)


class ScanOrchestrator:
    """
    Orchestrates vulnerability scanning by coordinating multiple agents.
    
    Pipeline:
    1. Scanner Agent: Run code analysis tools (bandit, semgrep)
    2. Threat Agent: Identify and categorize threat types
    3. Attack Agent: Plan attack scenarios
    4. Patch Agent: Generate code fixes
    5. Report Agent: Compile findings into report
    
    This orchestrator:
    - Manages agent execution order
    - Passes output from one agent as input to the next
    - Updates scan progress
    - Handles errors and rollback
    - Maintains execution logs
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize orchestrator.
        
        Args:
            session: AsyncSession for database operations
        """
        self.session = session
        self.logger = logging.getLogger(__name__)
        self.agents: List[BaseAgent] = []
        self.results: List[AgentOutput] = []
    
    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent to be executed in order.
        
        Args:
            agent: BaseAgent instance
        """
        self.agents.append(agent)
        self.logger.info(f"Registered agent: {agent.name}")
    
    async def update_scan_progress(
        self,
        scan_id: str,
        progress: int,
        status: Optional[str] = None
    ) -> None:
        """
        Update scan progress and status.
        
        Args:
            scan_id: Scan ID
            progress: Progress percentage (0-100)
            status: Optional new status
        """
        try:
            scan = await self.session.get(Scan, scan_id)
            if not scan:
                self.logger.warning(f"Scan {scan_id} not found")
                return
            
            scan.progress = min(progress, 100)
            
            if status:
                scan.status = status
            
            scan.updated_at = datetime.now()
            await self.session.flush()
            
            self.logger.info(f"Updated scan {scan_id}: {progress}% - {status}")
        
        except Exception as e:
            self.logger.error(f"Failed to update scan progress: {e}")
    
    async def execute(
        self,
        scan_id: str,
        repository_id: str
    ) -> bool:
        """
        Execute the complete scan pipeline.
        
        Args:
            scan_id: Scan ID to process
            repository_id: Repository ID
            
        Returns:
            True if successful, False if failed
        """
        self.logger.info(f"Starting scan orchestration for {scan_id}")
        
        try:
            # Update scan to RUNNING
            await self.update_scan_progress(
                scan_id,
                progress=5,
                status=ScanStatus.RUNNING
            )
            
            # Prepare base input
            input_data = AgentInput(
                scan_id=scan_id,
                repository_id=repository_id
            )
            
            # Execute agents sequentially
            total_agents = len(self.agents)
            
            for index, agent in enumerate(self.agents):
                self.logger.info(f"Executing agent {index + 1}/{total_agents}: {agent.name}")
                
                # Calculate progress (each agent gets ~15% increments)
                progress = 5 + (index * 15)
                await self.update_scan_progress(scan_id, progress)
                
                try:
                    # Execute agent
                    output = await agent.execute(input_data)
                    self.results.append(output)
                    
                    if not output.success:
                        self.logger.error(
                            f"Agent {agent.name} failed: {output.error}"
                        )
                        # Continue to next agent instead of aborting
                        # This allows partial results
                        continue
                    
                    self.logger.info(
                        f"Agent {agent.name} completed: {output.message}"
                    )
                    
                    # Pass this agent's output to next agent
                    if output.data:
                        input_data = AgentInput(
                            scan_id=scan_id,
                            repository_id=repository_id,
                            **output.data
                        )
                
                except Exception as e:
                    self.logger.error(
                        f"Unexpected error in agent {agent.name}: {e}",
                        exc_info=True
                    )
                    # Log and continue
                    continue
            
            # Update scan to COMPLETED
            await self.update_scan_progress(
                scan_id,
                progress=100,
                status=ScanStatus.COMPLETED
            )
            
            self.logger.info(f"Scan {scan_id} completed successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Orchestration failed: {e}", exc_info=True)
            
            # Update scan to FAILED
            try:
                scan = await self.session.get(Scan, scan_id)
                if scan:
                    scan.status = ScanStatus.FAILED
                    scan.error_message = str(e)
                    scan.updated_at = datetime.now()
                    await self.session.flush()
            except Exception as flush_error:
                self.logger.error(f"Failed to update error status: {flush_error}")
            
            return False
    
    def get_results(self) -> List[AgentOutput]:
        """
        Get all agent results.
        
        Returns:
            List of AgentOutput from executed agents
        """
        return self.results
    
    def get_result_summary(self) -> Dict[str, Any]:
        """
        Get summary of all agent results.
        
        Returns:
            Summary dict with success count, error count, messages
        """
        successful = sum(1 for r in self.results if r.success)
        failed = sum(1 for r in self.results if not r.success)
        
        return {
            "total_agents": len(self.agents),
            "executed_agents": len(self.results),
            "successful": successful,
            "failed": failed,
            "agents": [
                {
                    "name": agent.name,
                    "success": result.success if i < len(self.results) else None,
                    "message": result.message if i < len(self.results) else None,
                    "execution_time_ms": result.execution_time_ms if i < len(self.results) else None
                }
                for i, agent in enumerate(self.agents)
                for result in ([self.results[i]] if i < len(self.results) else [])
            ]
        }

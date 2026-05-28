"""Base agent class for SentinelOS."""

from abc import ABC, abstractmethod
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.models import AgentLog
from app.utils.helpers import generate_id


logger = logging.getLogger(__name__)


class AgentInput(BaseModel):
    """Base input model for agents."""
    scan_id: str
    repository_id: Optional[str] = None
    
    class Config:
        """Pydantic config."""
        extra = "allow"


class AgentOutput(BaseModel):
    """Base output model for agents."""
    success: bool
    step: int
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
    
    class Config:
        """Pydantic config."""
        extra = "allow"


class BaseAgent(ABC):
    """
    Abstract base class for all SentinelOS agents.
    
    Agents are responsible for specific analysis and simulation tasks:
    - Scanner Agent: Run code analysis tools (bandit, semgrep)
    - Threat Agent: Identify and categorize threats
    - Attack Agent: Simulate attack scenarios
    - Patch Agent: Generate code fixes
    - Report Agent: Compile findings into reports
    
    All agents follow the same lifecycle:
    1. validate_input() - Ensure inputs are correct
    2. execute() - Main agent logic (calls process())
    3. format_output() - Structure results
    4. log_execution() - Record to database
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize agent.
        
        Args:
            session: AsyncSession for database operations
        """
        self.session = session
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = self.__class__.__name__
        self.step = 0
    
    @abstractmethod
    async def process(self, input_data: AgentInput) -> Dict[str, Any]:
        """
        Core processing logic. Must be implemented by subclasses.
        
        Args:
            input_data: Agent input
            
        Returns:
            Processing results as dict
        """
        pass
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Execute agent with full error handling and logging.
        
        Args:
            input_data: Agent input
            
        Returns:
            AgentOutput with results
        """
        start_time = datetime.now()
        self.step += 1
        
        try:
            # Validate input
            await self.validate_input(input_data)
            self.logger.info(f"[{self.name}] Input validated for scan {input_data.scan_id}")
            
            # Process
            self.logger.info(f"[{self.name}] Starting processing...")
            data = await self.process(input_data)
            
            # Format output
            output = await self.format_output(data)
            
            # Calculate execution time
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Log execution
            await self.log_execution(
                scan_id=input_data.scan_id,
                message=output["message"],
                log_level="INFO",
                execution_time_ms=execution_time_ms,
                details={"data": output.get("data")}
            )
            
            self.logger.info(
                f"[{self.name}] Step {self.step} completed in {execution_time_ms}ms"
            )
            
            return AgentOutput(
                success=True,
                step=self.step,
                message=output["message"],
                data=output.get("data"),
                execution_time_ms=execution_time_ms
            )
        
        except Exception as e:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            error_msg = f"{self.name} failed: {str(e)}"
            
            self.logger.error(error_msg, exc_info=True)
            
            # Log error
            await self.log_execution(
                scan_id=input_data.scan_id,
                message=error_msg,
                log_level="ERROR",
                execution_time_ms=execution_time_ms,
                details={"error": str(e)}
            )
            
            return AgentOutput(
                success=False,
                step=self.step,
                message=error_msg,
                error=str(e),
                execution_time_ms=execution_time_ms
            )
    
    async def validate_input(self, input_data: AgentInput) -> None:
        """
        Validate input data. Override in subclass for custom validation.
        
        Args:
            input_data: Agent input
            
        Raises:
            ValueError: If validation fails
        """
        if not input_data.scan_id:
            raise ValueError("scan_id is required")
    
    async def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw processing output. Override in subclass for custom formatting.
        
        Args:
            data: Raw data from process()
            
        Returns:
            Formatted output dict with 'message' and 'data' keys
        """
        return {
            "message": "Processing completed",
            "data": data
        }
    
    async def log_execution(
        self,
        scan_id: str,
        message: str,
        log_level: str = "INFO",
        execution_time_ms: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log agent execution to database.
        
        Args:
            scan_id: Scan ID
            message: Log message
            log_level: DEBUG, INFO, WARN, ERROR
            execution_time_ms: Execution time in milliseconds
            details: JSON details
        """
        try:
            log_entry = AgentLog(
                id=generate_id(),
                scan_id=scan_id,
                agent_name=self.name,
                agent_step=self.step,
                log_level=log_level,
                message=message,
                details=details or {},
                execution_time_ms=execution_time_ms,
                timestamp=datetime.now()
            )
            self.session.add(log_entry)
            await self.session.flush()
        except Exception as e:
            self.logger.error(f"Failed to log execution: {e}")
    
    async def get_scan(self):
        """Get the current scan from database."""
        from app.models import Scan
        from sqlalchemy import select
        
        # Get from first step's input - this should be overridden if needed
        raise NotImplementedError("Override in subclass if scan lookup needed")

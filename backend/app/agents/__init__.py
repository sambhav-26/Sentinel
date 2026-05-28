"""Agent module initialization."""

from app.agents.base import BaseAgent, AgentInput, AgentOutput
from app.agents.scanner_agent import ScannerAgent
from app.agents.threat_agent import ThreatAgent
from app.agents.attack_agent import AttackAgent
from app.agents.patch_agent import PatchAgent
from app.agents.report_agent import ReportAgent

__all__ = [
    "BaseAgent",
    "AgentInput",
    "AgentOutput",
    "ScannerAgent",
    "ThreatAgent",
    "AttackAgent",
    "PatchAgent",
    "ReportAgent",
]

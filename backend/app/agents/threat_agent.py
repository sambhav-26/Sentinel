"""Threat classification agent."""

import logging
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.agents.base import BaseAgent, AgentInput
from app.models import Scan, Finding, SeverityLevel
from app.utils.cwe_mapping import get_cwe_mapping

logger = logging.getLogger(__name__)


# Threat classification rules
THREAT_RULES = {
    "injection": {
        "keywords": ["sql", "injection", "command", "os command", "nosql"],
        "base_severity": 3,  # High
        "tactic": "Execution"
    },
    "cryptography": {
        "keywords": ["crypto", "md5", "sha1", "weak", "encryption"],
        "base_severity": 2,  # Medium
        "tactic": "Defense Evasion"
    },
    "authentication": {
        "keywords": ["password", "hardcoded", "secret", "api key", "token"],
        "base_severity": 3,  # High
        "tactic": "Credential Access"
    },
    "dangerous_execution": {
        "keywords": ["exec", "eval", "subprocess", "dangerous"],
        "base_severity": 3,  # High
        "tactic": "Execution"
    },
    "misconfiguration": {
        "keywords": ["debug", "insecure", "exposed", "misconfiguration"],
        "base_severity": 2,  # Medium
        "tactic": "Discovery"
    }
}


class ThreatAgent(BaseAgent):
    """
    Threat classification and analysis agent.
    
    This agent:
    1. Fetches findings from scanner
    2. Classifies threats (threat type, severity, MITRE tactics)
    3. Assigns exploitability and impact scores
    4. Updates findings with threat data
    
    Output: Enhanced findings with threat metadata
    """
    
    async def process(self, input_data: AgentInput) -> Dict[str, Any]:
        """
        Classify and analyze threats in findings.
        
        Returns:
            Dict with threat analysis results
        """
        scan_id = input_data.scan_id
        self.logger.info(f"Analyzing threats for scan: {scan_id}")
        
        # Get all findings for this scan
        query = select(Finding).where(Finding.scan_id == scan_id)
        result = await self.session.execute(query)
        findings = result.scalars().all()
        
        self.logger.info(f"Analyzing {len(findings)} findings")
        
        threat_data = []
        
        for finding in findings:
            # Classify threat type
            threat_type = self._classify_threat(finding)
            
            # Update finding with threat metadata
            finding.custom_metadata = finding.custom_metadata or {}
            finding.custom_metadata["threat_type"] = threat_type
            finding.updated_at = datetime.now()
            
            threat_data.append({
                "finding_id": finding.id,
                "file_path": finding.file_path,
                "vulnerability_type": finding.vulnerability_type,
                "severity": finding.severity,
                "threat_type": threat_type,
                "exploitability_score": finding.exploitability_score,
                "cwe_id": finding.cwe_id,
            })
        
        await self.session.flush()
        
        # Calculate threat statistics
        threat_counts = {}
        for threat in threat_data:
            threat_type = threat["threat_type"]
            threat_counts[threat_type] = threat_counts.get(threat_type, 0) + 1
        
        self.logger.info(f"Threat classification complete: {threat_counts}")
        
        # Update scan progress
        scan = await self.session.get(Scan, scan_id)
        if scan:
            scan.progress = 40
            scan.updated_at = datetime.now()
            await self.session.flush()
        
        return {
            "threats": threat_data,
            "threat_counts": threat_counts,
            "findings_count": len(findings)
        }
    
    async def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format output for next agent."""
        total_threats = sum(data["threat_counts"].values())
        return {
            "message": f"Threat analysis complete: {total_threats} threats classified",
            "data": {
                "threats": data["threats"],
                "threat_counts": data["threat_counts"],
                "findings_count": data["findings_count"]
            }
        }
    
    def _classify_threat(self, finding: Finding) -> str:
        """
        Classify finding into threat category.
        
        Args:
            finding: Finding object
            
        Returns:
            Threat type classification
        """
        vuln_type = finding.vulnerability_type.lower()
        description = (finding.description or "").lower()
        
        # Check against threat rules
        for threat_name, rule in THREAT_RULES.items():
            for keyword in rule["keywords"]:
                if keyword in vuln_type or keyword in description:
                    return threat_name
        
        # Default classification based on severity
        if finding.severity == "critical":
            return "critical_vulnerability"
        elif finding.severity == "high":
            return "high_severity"
        elif finding.severity == "medium":
            return "medium_severity"
        else:
            return "low_severity"
    
    def _calculate_exploitability(self, finding: Finding) -> float:
        """
        Calculate exploitability score for finding.
        
        Args:
            finding: Finding object
            
        Returns:
            Exploitability score 0-1
        """
        score = finding.exploitability_score or 0.5
        
        # Boost score based on severity
        severity_boost = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2,
            "info": 0.1,
        }
        
        boost = severity_boost.get(finding.severity, 0.5)
        return min(score * boost, 1.0)
    
    def _calculate_impact(self, finding: Finding) -> float:
        """
        Calculate potential impact score.
        
        Args:
            finding: Finding object
            
        Returns:
            Impact score 0-10
        """
        impact = 5.0  # Default medium impact
        
        # Adjust based on severity
        if finding.severity == "critical":
            impact = 9.0
        elif finding.severity == "high":
            impact = 7.0
        elif finding.severity == "medium":
            impact = 5.0
        elif finding.severity == "low":
            impact = 3.0
        else:
            impact = 1.0
        
        return impact

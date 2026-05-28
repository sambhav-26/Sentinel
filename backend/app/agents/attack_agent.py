"""Attack simulation agent."""

import logging
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.agents.base import BaseAgent, AgentInput
from app.models import Scan, Finding, Attack
from app.utils.helpers import generate_id
from app.utils.mitre_mapping import get_mitre_technique

logger = logging.getLogger(__name__)


# Attack simulation templates
ATTACK_TEMPLATES = {
    "SQL Injection": {
        "attack_type": "SQL Injection",
        "attack_vector": "Network",
        "success_probability": 0.85,
        "impact_score": 9.5,
        "mitre_technique": "T1190",  # Exploit Public-Facing Application
        "tactic": "Initial Access",
        "attack_steps": [
            "Identify vulnerable input field",
            "Craft malicious SQL payload",
            "Execute payload through vulnerable endpoint",
            "Retrieve sensitive data from database",
        ],
        "prerequisites": ["Web application accepting user input", "Vulnerable query construction"],
        "mitigation": "Use parameterized queries and input validation",
    },
    "Authentication Bypass": {
        "attack_type": "Authentication Bypass",
        "attack_vector": "Network",
        "success_probability": 0.7,
        "impact_score": 8.5,
        "mitre_technique": "T1110",  # Brute Force
        "tactic": "Credential Access",
        "attack_steps": [
            "Discover authentication mechanism",
            "Attempt default credentials",
            "Exploit weak password policy",
            "Gain unauthorized access",
        ],
        "prerequisites": ["Weak password policy", "No account lockout"],
        "mitigation": "Implement strong password requirements and rate limiting",
    },
    "Remote Code Execution": {
        "attack_type": "Remote Code Execution",
        "attack_vector": "Network",
        "success_probability": 0.9,
        "impact_score": 10.0,
        "mitre_technique": "T1203",  # Exploitation for Client Execution
        "tactic": "Execution",
        "attack_steps": [
            "Identify code execution vulnerability",
            "Prepare malicious payload",
            "Execute payload on target",
            "Establish reverse shell or web shell",
            "Execute arbitrary commands",
        ],
        "prerequisites": ["Vulnerable code path", "Ability to upload/inject code"],
        "mitigation": "Avoid unsafe functions (exec, eval), validate input, use sandboxing",
    },
    "Privilege Escalation": {
        "attack_type": "Privilege Escalation",
        "attack_vector": "Local",
        "success_probability": 0.6,
        "impact_score": 8.0,
        "mitre_technique": "T1548",  # Abuse Elevation Control Mechanism
        "tactic": "Privilege Escalation",
        "attack_steps": [
            "Gain initial access to system",
            "Identify privilege escalation vector",
            "Exploit vulnerability or misconfiguration",
            "Obtain elevated privileges",
        ],
        "prerequisites": ["Initial system access", "Unpatched vulnerability"],
        "mitigation": "Apply security patches, follow least privilege principle",
    },
}


class AttackAgent(BaseAgent):
    """
    Attack simulation and scenario planning agent.
    
    This agent:
    1. Fetches findings from threat analysis
    2. Plans attack scenarios for each vulnerability
    3. Assesses attack success probability and impact
    4. Maps to MITRE ATT&CK framework
    5. Creates attack records in database
    
    Output: Attack scenarios and exploitation paths
    """
    
    async def process(self, input_data: AgentInput) -> Dict[str, Any]:
        """
        Simulate attacks and create exploitation scenarios.
        
        Returns:
            Dict with attack scenarios
        """
        scan_id = input_data.scan_id
        self.logger.info(f"Planning attacks for scan: {scan_id}")
        
        # Get all findings
        query = select(Finding).where(Finding.scan_id == scan_id)
        result = await self.session.execute(query)
        findings = result.scalars().all()
        
        self.logger.info(f"Planning attacks for {len(findings)} findings")
        
        attacks_created = 0
        
        for finding in findings:
            try:
                # Get attack template or create custom attack
                attack_data = self._plan_attack(finding)
                
                # Create attack record
                technique_id = attack_data.get("mitre_technique", "T0000")
                technique_name, tactic = get_mitre_technique(technique_id)
                
                attack = Attack(
                    id=generate_id(),
                    scan_id=scan_id,
                    finding_id=finding.id,
                    attack_type=attack_data["attack_type"],
                    attack_vector=attack_data.get("attack_vector", "Network"),
                    success_probability=attack_data.get("success_probability", 0.5),
                    impact_score=attack_data.get("impact_score", 5.0),
                    mitre_technique=technique_id,
                    mitre_tactic=attack_data.get("tactic", "Initial Access"),
                    attack_path=attack_data.get("attack_steps", []),
                    impact_description=self._describe_impact(finding, attack_data),
                    prerequisites=attack_data.get("prerequisites", []),
                    mitigation=attack_data.get("mitigation", "Apply security patches"),
                    metadata={
                        "vulnerability_type": finding.vulnerability_type,
                        "severity": finding.severity,
                    },
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
                
                self.session.add(attack)
                attacks_created += 1
                
            except Exception as e:
                self.logger.error(f"Failed to create attack for finding {finding.id}: {e}")
        
        await self.session.flush()
        
        self.logger.info(f"Created {attacks_created} attack scenarios")
        
        # Update scan progress
        scan = await self.session.get(Scan, scan_id)
        if scan:
            scan.progress = 60
            scan.updated_at = datetime.now()
            await self.session.flush()
        
        return {
            "attacks_count": attacks_created,
            "findings_analyzed": len(findings)
        }
    
    async def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format output for next agent."""
        return {
            "message": f"Attack planning complete: {data['attacks_count']} attack scenarios created",
            "data": {
                "attacks_count": data["attacks_count"],
                "findings_analyzed": data["findings_analyzed"]
            }
        }
    
    def _plan_attack(self, finding: Finding) -> Dict[str, Any]:
        """
        Plan attack scenario for a finding.
        
        Args:
            finding: Finding object
            
        Returns:
            Attack data dict
        """
        vuln_type = finding.vulnerability_type
        
        # Look for matching template
        for template_type, template in ATTACK_TEMPLATES.items():
            if template_type.lower() in vuln_type.lower():
                return template.copy()
        
        # Create generic attack scenario
        return {
            "attack_type": f"Exploit {finding.vulnerability_type}",
            "attack_vector": "Network",
            "success_probability": self._calculate_success_probability(finding),
            "impact_score": self._calculate_impact_score(finding),
            "mitre_technique": "T1190",  # Default to public-facing app
            "tactic": "Initial Access",
            "attack_steps": [
                f"Identify {finding.vulnerability_type} vulnerability",
                "Craft exploitation payload",
                "Execute attack against vulnerable code",
                "Achieve attack objective",
            ],
            "prerequisites": ["Network access to application"],
            "mitigation": "Apply patches and code fixes",
        }
    
    def _calculate_success_probability(self, finding: Finding) -> float:
        """
        Calculate probability of successful attack.
        
        Args:
            finding: Finding object
            
        Returns:
            Success probability 0-1
        """
        base = 0.5
        
        # Increase probability based on severity
        if finding.severity == "critical":
            base = 0.95
        elif finding.severity == "high":
            base = 0.85
        elif finding.severity == "medium":
            base = 0.65
        elif finding.severity == "low":
            base = 0.35
        
        # Factor in exploitability score
        exploitability = finding.exploitability_score or 0.5
        return min(base * (exploitability + 0.5), 1.0)
    
    def _calculate_impact_score(self, finding: Finding) -> float:
        """
        Calculate potential impact of successful attack.
        
        Args:
            finding: Finding object
            
        Returns:
            Impact score 0-10
        """
        base_impacts = {
            "critical": 9.5,
            "high": 8.0,
            "medium": 6.0,
            "low": 3.0,
            "info": 1.0,
        }
        
        return base_impacts.get(finding.severity, 5.0)
    
    def _describe_impact(self, finding: Finding, attack_data: Dict[str, Any]) -> str:
        """
        Create detailed impact description.
        
        Args:
            finding: Finding object
            attack_data: Attack data dict
            
        Returns:
            Impact description string
        """
        impact = f"Successful exploitation of {finding.vulnerability_type} could allow "
        
        if "SQL" in finding.vulnerability_type:
            impact += "unauthorized database access and data theft."
        elif "Command" in finding.vulnerability_type or "Execution" in finding.vulnerability_type:
            impact += "remote code execution and complete system compromise."
        elif "Authentication" in finding.vulnerability_type:
            impact += "unauthorized account access and privilege escalation."
        elif "Password" in finding.vulnerability_type or "Secret" in finding.vulnerability_type:
            impact += "credential compromise and lateral movement."
        elif "Crypto" in finding.vulnerability_type:
            impact += "encryption key recovery and data exposure."
        else:
            impact += "security breach and potential data exposure."
        
        return impact

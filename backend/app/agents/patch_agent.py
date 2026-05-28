"""Patch generation agent."""

import logging
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.agents.base import BaseAgent, AgentInput
from app.models import Scan, Finding, Patch
from app.utils.helpers import generate_id

logger = logging.getLogger(__name__)


# Patch templates for common vulnerabilities
PATCH_TEMPLATES = {
    "SQL Injection": {
        "original_pattern": "query = f\"SELECT * FROM users WHERE id = {user_id}\"",
        "patched_pattern": "query = \"SELECT * FROM users WHERE id = ?\"; execute(query, (user_id,))",
        "explanation": "Use parameterized queries to prevent SQL injection",
        "approach": "Replace string formatting with parameterized query",
    },
    "Hardcoded Password": {
        "original_pattern": 'password = "secretpass123"',
        "patched_pattern": "password = os.getenv('PASSWORD')",
        "explanation": "Move secrets from code to environment variables",
        "approach": "Use environment variables or secrets management",
    },
    "Weak Cryptography": {
        "original_pattern": "hashlib.md5(data).hexdigest()",
        "patched_pattern": "hashlib.sha256(data).hexdigest()",
        "explanation": "MD5 is cryptographically weak. Use SHA-256 or bcrypt",
        "approach": "Replace weak hash with stronger algorithm",
    },
    "Dangerous Code Execution": {
        "original_pattern": "exec(user_input)",
        "patched_pattern": "# Use safer alternatives like ast.literal_eval() for specific cases",
        "explanation": "Avoid exec() and eval(). Use safer parsing methods",
        "approach": "Replace exec/eval with safer alternatives",
    },
}


class PatchAgent(BaseAgent):
    """
    Patch generation and remediation suggestions agent.
    
    This agent:
    1. Fetches findings to patch
    2. Generates code fixes (AI or template-based)
    3. Assesses patch applicability and safety
    4. Creates patch records in database
    5. Estimates remediation effort
    
    Output: Suggested code patches
    """
    
    async def process(self, input_data: AgentInput) -> Dict[str, Any]:
        """
        Generate patches for vulnerabilities.
        
        Returns:
            Dict with patch suggestions
        """
        scan_id = input_data.scan_id
        self.logger.info(f"Generating patches for scan: {scan_id}")
        
        # Get all findings
        query = select(Finding).where(Finding.scan_id == scan_id)
        result = await self.session.execute(query)
        findings = result.scalars().all()
        
        self.logger.info(f"Generating patches for {len(findings)} findings")
        
        patches_created = 0
        
        for finding in findings:
            try:
                # Generate patch for finding
                patch_data = self._generate_patch(finding)
                
                # Create patch record
                patch = Patch(
                    id=generate_id(),
                    scan_id=scan_id,
                    finding_id=finding.id,
                    original_code=patch_data["original_code"],
                    patched_code=patch_data["patched_code"],
                    explanation=patch_data["explanation"],
                    additional_context=patch_data.get("additional_context"),
                    is_ai_generated=patch_data.get("is_ai_generated", False),
                    confidence=patch_data.get("confidence", 0.7),
                    can_auto_apply=patch_data.get("can_auto_apply", False),
                    apply_complexity=patch_data.get("apply_complexity", "moderate"),
                    applied=False,
                    metadata={
                        "vulnerability_type": finding.vulnerability_type,
                        "severity": finding.severity,
                        "approach": patch_data.get("approach"),
                    },
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
                
                self.session.add(patch)
                patches_created += 1
                
            except Exception as e:
                self.logger.error(f"Failed to create patch for finding {finding.id}: {e}")
        
        await self.session.flush()
        
        self.logger.info(f"Created {patches_created} patch suggestions")
        
        # Update scan progress
        scan = await self.session.get(Scan, scan_id)
        if scan:
            scan.progress = 80
            scan.updated_at = datetime.now()
            await self.session.flush()
        
        return {
            "patches_count": patches_created,
            "findings_analyzed": len(findings)
        }
    
    async def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format output for next agent."""
        return {
            "message": f"Patch generation complete: {data['patches_count']} patches created",
            "data": {
                "patches_count": data["patches_count"],
                "findings_analyzed": data["findings_analyzed"]
            }
        }
    
    def _generate_patch(self, finding: Finding) -> Dict[str, Any]:
        """
        Generate patch for a finding.
        
        Args:
            finding: Finding object
            
        Returns:
            Patch data dict
        """
        vuln_type = finding.vulnerability_type
        
        # Look for matching template
        for template_type, template in PATCH_TEMPLATES.items():
            if template_type.lower() in vuln_type.lower():
                return {
                    "original_code": template["original_pattern"],
                    "patched_code": template["patched_pattern"],
                    "explanation": template["explanation"],
                    "additional_context": f"File: {finding.file_path}\nLine: {finding.line_number}",
                    "approach": template["approach"],
                    "is_ai_generated": False,
                    "confidence": 0.85,
                    "can_auto_apply": False,
                    "apply_complexity": "simple",
                }
        
        # Generate generic patch
        return {
            "original_code": finding.code_snippet or f"# Code at {finding.file_path}:{finding.line_number}",
            "patched_code": "# Apply the fix recommended below\n# " + (finding.recommendation or "See security advisory"),
            "explanation": f"Fix for {finding.vulnerability_type}: {finding.description}",
            "additional_context": finding.recommendation or "Review security best practices",
            "approach": "Custom fix required",
            "is_ai_generated": False,
            "confidence": 0.6,
            "can_auto_apply": False,
            "apply_complexity": "complex",
        }
    
    def _estimate_complexity(self, finding: Finding) -> str:
        """
        Estimate complexity of applying patch.
        
        Args:
            finding: Finding object
            
        Returns:
            Complexity level: "simple", "moderate", "complex"
        """
        vuln_type = finding.vulnerability_type.lower()
        
        # Simple fixes
        if "password" in vuln_type or "hardcoded" in vuln_type:
            return "simple"
        
        # Moderate fixes
        if "import" in vuln_type or "crypto" in vuln_type:
            return "moderate"
        
        # Complex fixes
        return "complex"
    
    def _estimate_risk(self, finding: Finding) -> float:
        """
        Estimate risk of applying patch incorrectly.
        
        Args:
            finding: Finding object
            
        Returns:
            Risk score 0-1
        """
        if finding.severity == "critical":
            return 0.1  # High value on fixing, low risk tolerance
        elif finding.severity == "high":
            return 0.2
        elif finding.severity == "medium":
            return 0.4
        else:
            return 0.6

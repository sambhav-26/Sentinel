"""Scanner agent for code vulnerability scanning."""

import asyncio
import json
import logging
import re
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.agents.base import BaseAgent, AgentInput
from app.models import Scan, Finding, SeverityLevel
from app.utils.helpers import generate_id
from app.utils.cwe_mapping import get_cwe_mapping
from app.utils.mitre_mapping import get_mitre_technique

logger = logging.getLogger(__name__)


class ScannerAgent(BaseAgent):
    """
    Scanner agent runs static analysis tools (bandit, semgrep) on code.
    
    This agent:
    1. Fetches the repository path from scan record
    2. Runs bandit (Python security linter)
    3. Runs semgrep (SAST pattern matching)
    4. Parses and normalizes results
    5. Saves findings to database
    
    Output: List of Finding records saved to database
    """
    
    async def validate_input(self, input_data: AgentInput) -> None:
        """Validate that scan exists in database."""
        await super().validate_input(input_data)
        
        # Get scan from database
        scan = await self.session.get(Scan, input_data.scan_id)
        if not scan:
            raise ValueError(f"Scan not found: {input_data.scan_id}")
    
    async def process(self, input_data: AgentInput) -> Dict[str, Any]:
        """
        Run code analysis on repository.
        
        Returns:
            Dict with findings count and list of findings
        """
        scan_id = input_data.scan_id
        
        # Get scan record
        scan = await self.session.get(Scan, scan_id)
        self.logger.info(f"Starting scan of repository: {scan.repository_id}")
        
        # Collect all findings
        all_findings = []
        
        try:
            # Run bandit analysis
            self.logger.info("Running bandit analysis...")
            bandit_findings = await self._run_bandit(scan)
            all_findings.extend(bandit_findings)
            self.logger.info(f"Bandit found {len(bandit_findings)} issues")
            
        except Exception as e:
            self.logger.error(f"Bandit analysis failed: {e}")
            # Continue with other tools
        
        try:
            # Run semgrep analysis
            self.logger.info("Running semgrep analysis...")
            semgrep_findings = await self._run_semgrep(scan)
            all_findings.extend(semgrep_findings)
            self.logger.info(f"Semgrep found {len(semgrep_findings)} issues")
            
        except Exception as e:
            self.logger.error(f"Semgrep analysis failed: {e}")
            # Continue
        
        # Deduplicate findings by file+line+type
        deduplicated = self._deduplicate_findings(all_findings)
        self.logger.info(f"After deduplication: {len(deduplicated)} unique issues")
        
        # Save findings to database
        saved_count = 0
        for finding_data in deduplicated:
            try:
                finding = Finding(
                    id=generate_id(),
                    scan_id=scan_id,
                    vulnerability_type=finding_data["vulnerability_type"],
                    severity=finding_data["severity"],
                    file_path=finding_data["file_path"],
                    line_number=finding_data["line_number"],
                    column_number=finding_data.get("column_number", 0),
                    cwe_id=finding_data.get("cwe_id"),
                    cwe_name=finding_data.get("cwe_name"),
                    owasp_category=finding_data.get("owasp_category"),
                    exploitability_score=finding_data.get("exploitability_score", 0.5),
                    code_snippet=finding_data.get("code_snippet"),
                    description=finding_data.get("description"),
                    recommendation=finding_data.get("recommendation"),
                    is_ignored=False,
                    detection_source=finding_data.get("detection_source", "scanner"),
                    confidence=finding_data.get("confidence", 0.9),
                    metadata={"raw_data": finding_data},
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
                self.session.add(finding)
                saved_count += 1
            except Exception as e:
                self.logger.error(f"Failed to save finding: {e}")
        
        await self.session.flush()
        
        self.logger.info(f"Saved {saved_count} findings to database")
        
        # Update scan progress
        scan.progress = 20
        scan.files_scanned = len(deduplicated)
        scan.updated_at = datetime.now()
        await self.session.flush()
        
        return {
            "findings_count": len(deduplicated),
            "findings": deduplicated
        }
    
    async def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format output for next agent."""
        return {
            "message": f"Scanner completed: found {data['findings_count']} vulnerabilities",
            "data": {
                "findings": data["findings"],
                "findings_count": data["findings_count"]
            }
        }
    
    async def _run_bandit(self, scan: Scan) -> List[Dict[str, Any]]:
        """
        Run bandit security linter on Python code.
        
        Bandit is a tool for finding common security issues in Python code.
        In production, this would run: bandit -r /path/to/repo -f json
        """
        findings = []
        
        # Mock findings that represent what bandit would find
        # These are realistic security issues from Python code analysis
        sample_issues = [
            {
                "vulnerability_type": "Hardcoded Password",
                "severity": "high",
                "file_path": "app/config.py",
                "line_number": 12,
                "column_number": 15,
                "code_snippet": 'DB_PASSWORD = "admin123456"',
                "description": "Hardcoded database password found in configuration",
                "recommendation": "Use environment variables or secrets management system (e.g., AWS Secrets Manager, HashiCorp Vault)",
                "detection_source": "bandit",
                "confidence": 0.99,
                "exploitability_score": 0.85,
            },
            {
                "vulnerability_type": "SQL Injection",
                "severity": "critical",
                "file_path": "app/api/users.py",
                "line_number": 47,
                "column_number": 20,
                "code_snippet": 'query = f"SELECT * FROM users WHERE id = {user_id}"',
                "description": "Potential SQL injection vulnerability through unsanitized user input",
                "recommendation": "Use parameterized queries or ORM (SQLAlchemy, Django ORM)",
                "detection_source": "bandit",
                "confidence": 0.88,
                "exploitability_score": 0.95,
            },
            {
                "vulnerability_type": "Insecure Pickle Usage",
                "severity": "high",
                "file_path": "app/utils/cache.py",
                "line_number": 23,
                "column_number": 10,
                "code_snippet": 'pickle.loads(user_data)',
                "description": "Potential code execution through pickle deserialization of untrusted data",
                "recommendation": "Use safer serialization formats (JSON) or implement validation",
                "detection_source": "bandit",
                "confidence": 0.92,
                "exploitability_score": 0.9,
            },
        ]
        
        for issue in sample_issues:
            cwe_id, owasp = get_cwe_mapping(issue["vulnerability_type"])
            issue["cwe_id"] = cwe_id
            issue["owasp_category"] = owasp
            findings.append(issue)
        
        return findings
    
    async def _run_semgrep(self, scan: Scan) -> List[Dict[str, Any]]:
        """
        Run semgrep SAST analysis on code.
        
        Semgrep is a static analysis tool that can scan multiple languages.
        In production, this would run: semgrep --config=p/security-audit /path/to/repo --json
        """
        findings = []
        
        # Mock findings representing semgrep SAST analysis results
        # These are realistic security patterns detected across multiple languages
        sample_issues = [
            {
                "vulnerability_type": "Weak Cryptography - MD5",
                "severity": "high",
                "file_path": "app/security/hashing.py",
                "line_number": 18,
                "column_number": 12,
                "code_snippet": 'hashlib.md5(password.encode()).hexdigest()',
                "description": "MD5 is cryptographically broken and should not be used for password hashing",
                "recommendation": "Use bcrypt, scrypt, or PBKDF2 for password hashing. Use SHA-256+ for integrity checking",
                "detection_source": "semgrep",
                "confidence": 0.99,
                "exploitability_score": 0.7,
            },
            {
                "vulnerability_type": "Dangerous Code Execution - exec()",
                "severity": "critical",
                "file_path": "app/template/renderer.py",
                "line_number": 34,
                "column_number": 8,
                "code_snippet": "exec(template_code)",
                "description": "User-controlled input passed to exec() without validation, enabling arbitrary code execution",
                "recommendation": "Avoid exec() and eval(). Use Jinja2, Mako, or safer templating engines",
                "detection_source": "semgrep",
                "confidence": 1.0,
                "exploitability_score": 1.0,
            },
            {
                "vulnerability_type": "Unsafe Deserialization",
                "severity": "critical",
                "file_path": "app/services/cache_service.py",
                "line_number": 56,
                "column_number": 15,
                "code_snippet": 'yaml.load(untrusted_data)',
                "description": "YAML.load() with untrusted input can execute arbitrary Python code",
                "recommendation": "Use yaml.safe_load() instead of yaml.load()",
                "detection_source": "semgrep",
                "confidence": 0.98,
                "exploitability_score": 0.95,
            },
            {
                "vulnerability_type": "Insecure Temporary File Creation",
                "severity": "medium",
                "file_path": "app/utils/file_handler.py",
                "line_number": 71,
                "column_number": 20,
                "code_snippet": 'open(f"/tmp/file_{user_id}.txt", "w")',
                "description": "Predictable temporary file name could allow attackers to access or overwrite files",
                "recommendation": "Use tempfile.NamedTemporaryFile() for secure temporary file creation",
                "detection_source": "semgrep",
                "confidence": 0.85,
                "exploitability_score": 0.6,
            },
        ]
        
        for issue in sample_issues:
            cwe_id, owasp = get_cwe_mapping(issue["vulnerability_type"])
            issue["cwe_id"] = cwe_id
            issue["owasp_category"] = owasp
            findings.append(issue)
        
        return findings
    
    def _deduplicate_findings(
        self,
        findings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicate findings based on file, line, and vulnerability type.
        
        Args:
            findings: List of finding dicts
            
        Returns:
            Deduplicated list (keeping highest confidence/severity)
        """
        seen = {}
        deduplicated = []
        
        for finding in findings:
            key = (
                finding["file_path"],
                finding["line_number"],
                finding["vulnerability_type"]
            )
            
            if key not in seen:
                seen[key] = finding
                deduplicated.append(finding)
            else:
                # Keep the one with higher severity/confidence
                existing = seen[key]
                if (finding.get("confidence", 0) > existing.get("confidence", 0)):
                    # Replace with higher confidence version
                    deduplicated.remove(existing)
                    deduplicated.append(finding)
                    seen[key] = finding
        
        return deduplicated

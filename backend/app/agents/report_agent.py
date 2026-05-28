"""Report generation agent."""

import logging
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.agents.base import BaseAgent, AgentInput
from app.models import Scan, Finding, Attack, Patch, Report
from app.utils.helpers import (
    generate_id,
    calculate_risk_score,
    estimate_remediation_time,
    group_findings_by_severity
)

logger = logging.getLogger(__name__)


class ReportAgent(BaseAgent):
    """
    Report generation and compilation agent.
    
    This agent:
    1. Compiles all findings, attacks, and patches
    2. Calculates risk metrics and statistics
    3. Creates executive summary
    4. Generates recommendations
    5. Creates report record in database
    
    Output: Comprehensive security report
    """
    
    async def process(self, input_data: AgentInput) -> Dict[str, Any]:
        """
        Generate comprehensive security report.
        
        Returns:
            Dict with report data
        """
        scan_id = input_data.scan_id
        self.logger.info(f"Generating report for scan: {scan_id}")
        
        # Get scan
        scan = await self.session.get(Scan, scan_id)
        if not scan:
            raise ValueError(f"Scan not found: {scan_id}")
        
        # Fetch all related data
        findings_result = await self.session.execute(
            select(Finding).where(Finding.scan_id == scan_id)
        )
        findings = findings_result.scalars().all()
        
        attacks_result = await self.session.execute(
            select(Attack).where(Attack.scan_id == scan_id)
        )
        attacks = attacks_result.scalars().all()
        
        patches_result = await self.session.execute(
            select(Patch).where(Patch.scan_id == scan_id)
        )
        patches = patches_result.scalars().all()
        
        self.logger.info(
            f"Compiling report: {len(findings)} findings, "
            f"{len(attacks)} attacks, {len(patches)} patches"
        )
        
        # Calculate metrics
        severity_counts = self._count_by_severity(findings)
        risk_score = calculate_risk_score(**severity_counts)
        remediation_time = estimate_remediation_time(**severity_counts)
        patch_coverage = self._calculate_patch_coverage(findings, patches)
        
        # Generate report sections
        executive_summary = self._generate_executive_summary(
            scan, findings, risk_score, severity_counts
        )
        detailed_findings = self._generate_detailed_findings(findings, attacks, patches)
        recommendations = self._generate_recommendations(findings, severity_counts)
        
        # Create report record
        report = Report(
            id=generate_id(),
            scan_id=scan_id,
            title=f"Security Scan Report - {scan.id[:8]}",
            summary=f"Scan completed with {len(findings)} vulnerabilities found",
            overall_risk_score=risk_score,
            critical_count=severity_counts.get("critical", 0),
            high_count=severity_counts.get("high", 0),
            medium_count=severity_counts.get("medium", 0),
            low_count=severity_counts.get("low", 0),
            patch_coverage=patch_coverage,
            remediation_effort=self._estimate_effort(remediation_time),
            estimated_remediation_time=remediation_time,
            executive_summary=executive_summary,
            detailed_findings=detailed_findings,
            recommendations=recommendations,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        self.session.add(report)
        await self.session.flush()
        
        self.logger.info(f"Report generated: Risk Score={risk_score:.1f}")
        
        # Update scan status
        scan.progress = 100
        scan.completed_at = datetime.now()
        scan.updated_at = datetime.now()
        await self.session.flush()
        
        return {
            "report_id": report.id,
            "risk_score": risk_score,
            "findings_count": len(findings),
            "severity_counts": severity_counts,
            "patch_coverage": patch_coverage,
        }
    
    async def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format output for completion."""
        return {
            "message": f"Report generated: Risk Score {data['risk_score']:.0f}/100 with "
                      f"{data['findings_count']} vulnerabilities",
            "data": data
        }
    
    def _count_by_severity(self, findings: List[Finding]) -> Dict[str, int]:
        """Count findings by severity."""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for finding in findings:
            if finding.severity in counts:
                counts[finding.severity] += 1
        return counts
    
    def _calculate_patch_coverage(
        self,
        findings: List[Finding],
        patches: List[Patch]
    ) -> float:
        """Calculate percentage of findings with patches."""
        if not findings:
            return 0.0
        
        patched = sum(1 for p in patches if p.finding_id)
        return (patched / len(findings)) * 100
    
    def _generate_executive_summary(
        self,
        scan: Scan,
        findings: List[Finding],
        risk_score: float,
        severity_counts: Dict[str, int]
    ) -> str:
        """Generate executive summary."""
        summary = f"""
SECURITY SCAN EXECUTIVE SUMMARY
===============================

Scan ID: {scan.id[:8]}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

RISK ASSESSMENT
---------------
Overall Risk Score: {risk_score:.0f}/100
Risk Level: {self._risk_level(risk_score)}

FINDINGS SUMMARY
----------------
Total Vulnerabilities: {len(findings)}
  - Critical: {severity_counts.get('critical', 0)}
  - High: {severity_counts.get('high', 0)}
  - Medium: {severity_counts.get('medium', 0)}
  - Low: {severity_counts.get('low', 0)}

RECOMMENDATIONS
---------------
1. Address all CRITICAL vulnerabilities immediately
2. Schedule remediation for HIGH severity issues
3. Plan patches for MEDIUM severity findings
4. Monitor LOW severity issues

For detailed findings and remediation guidance, see detailed section below.
"""
        return summary.strip()
    
    def _generate_detailed_findings(
        self,
        findings: List[Finding],
        attacks: List[Attack],
        patches: List[Patch]
    ) -> List[Dict[str, Any]]:
        """Generate detailed findings list."""
        detailed = []
        
        for finding in findings:
            # Find related attack and patch
            attack = next((a for a in attacks if a.finding_id == finding.id), None)
            patch = next((p for p in patches if p.finding_id == finding.id), None)
            
            detail = {
                "id": finding.id,
                "vulnerability": finding.vulnerability_type,
                "severity": finding.severity,
                "file": finding.file_path,
                "line": finding.line_number,
                "cwe": finding.cwe_id,
                "description": finding.description,
                "recommendation": finding.recommendation,
            }
            
            if attack:
                detail["attack"] = {
                    "type": attack.attack_type,
                    "probability": attack.success_probability,
                    "impact": attack.impact_score,
                }
            
            if patch:
                detail["patch"] = {
                    "id": patch.id,
                    "confidence": patch.confidence,
                    "complexity": patch.apply_complexity,
                }
            
            detailed.append(detail)
        
        return detailed
    
    def _generate_recommendations(
        self,
        findings: List[Finding],
        severity_counts: Dict[str, int]
    ) -> List[str]:
        """Generate remediation recommendations."""
        recommendations = []
        
        # Critical findings
        if severity_counts.get("critical", 0) > 0:
            recommendations.append(
                f"URGENT: Fix {severity_counts['critical']} critical vulnerabilities immediately. "
                "These could lead to complete system compromise."
            )
        
        # High findings
        if severity_counts.get("high", 0) > 0:
            recommendations.append(
                f"HIGH PRIORITY: Address {severity_counts['high']} high-severity issues within 7 days. "
                "These require escalated attention but may take longer to patch."
            )
        
        # Medium findings
        if severity_counts.get("medium", 0) > 0:
            recommendations.append(
                f"MEDIUM PRIORITY: Plan remediation for {severity_counts['medium']} medium-severity issues "
                "within 30 days as part of regular maintenance."
            )
        
        # General recommendations
        recommendations.extend([
            "Implement secure coding practices and security training for development team",
            "Use static analysis tools in CI/CD pipeline to catch issues earlier",
            "Conduct regular security audits and penetration testing",
            "Keep all dependencies and frameworks up to date",
            "Use secrets management for API keys, passwords, and credentials",
        ])
        
        return recommendations
    
    def _risk_level(self, score: float) -> str:
        """Map risk score to level."""
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        elif score >= 20:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _estimate_effort(self, hours: int) -> str:
        """Estimate remediation effort."""
        if hours >= 40:
            return "high"
        elif hours >= 16:
            return "medium"
        else:
            return "low"

"""Utility helper functions."""

import uuid
from datetime import datetime
from typing import Any, Dict, List


def generate_id() -> str:
    """Generate a UUID string for database records."""
    return str(uuid.uuid4())


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO 8601 string."""
    if dt is None:
        return None
    return dt.isoformat()


def calculate_risk_score(
    critical: int = 0,
    high: int = 0,
    medium: int = 0,
    low: int = 0,
) -> float:
    """
    Calculate overall risk score (0-100) based on finding counts.
    
    Args:
        critical: Count of critical findings
        high: Count of high findings
        medium: Count of medium findings
        low: Count of low findings
        
    Returns:
        Risk score from 0 to 100
    """
    # Weighted scoring
    score = (critical * 25) + (high * 15) + (medium * 8) + (low * 2)
    # Cap at 100
    return min(score, 100.0)


def group_findings_by_severity(findings: List[Dict[str, Any]]) -> Dict[str, List]:
    """
    Group findings by severity level.
    
    Args:
        findings: List of finding dicts
        
    Returns:
        Dict with severity keys and finding lists
    """
    grouped = {
        "critical": [],
        "high": [],
        "medium": [],
        "low": [],
        "info": [],
    }
    
    for finding in findings:
        severity = finding.get("severity", "info").lower()
        if severity in grouped:
            grouped[severity].append(finding)
    
    return grouped


def estimate_remediation_time(
    critical: int = 0,
    high: int = 0,
    medium: int = 0,
    low: int = 0,
) -> int:
    """
    Estimate remediation time in hours based on finding counts.
    
    Args:
        critical: Count of critical findings
        high: Count of high findings
        medium: Count of medium findings
        low: Count of low findings
        
    Returns:
        Estimated hours
    """
    hours = (critical * 8) + (high * 4) + (medium * 2) + (low * 0.5)
    return int(hours)


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to max length and add ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

"""
Pydantic request/response schemas for API validation and documentation.

These schemas define:
- Request validation (what clients send)
- Response serialization (what API returns)
- Type hints and documentation
"""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, EmailStr

# ============================================================================
# Scan Schemas
# ============================================================================


class ScanCreate(BaseModel):
    """Request model for creating a new scan."""
    repository_url: str = Field(..., description="GitHub/GitLab repository URL")
    scan_type: str = Field(default="full", description="full or quick scan")


class ScanResponse(BaseModel):
    """Response model for scan."""
    id: str
    status: str  # queued, running, completed, failed
    progress: int = 0
    total_files: int = 0
    files_scanned: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScanDetailResponse(ScanResponse):
    """Extended scan response with findings summary."""
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    total_findings: int = 0


# ============================================================================
# Finding Schemas
# ============================================================================


class FindingResponse(BaseModel):
    """Response model for vulnerability finding."""
    id: str
    scan_id: str
    vulnerability_type: str
    severity: str  # critical, high, medium, low, info
    file_path: str
    line_number: int
    column_number: int = 0
    cwe_id: Optional[str] = None
    cwe_name: Optional[str] = None
    owasp_category: Optional[str] = None
    exploitability_score: float = 0.0
    code_snippet: Optional[str] = None
    description: Optional[str] = None
    recommendation: Optional[str] = None
    is_ignored: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FindingDetailResponse(FindingResponse):
    """Extended finding response with related data."""
    attack: Optional[Any] = None
    patch: Optional[Any] = None


# ============================================================================
# Attack Schemas
# ============================================================================


class AttackResponse(BaseModel):
    """Response model for attack simulation."""
    id: str
    scan_id: str
    finding_id: Optional[str] = None
    attack_type: str
    attack_vector: Optional[str] = None
    success_probability: float = 0.0
    impact_score: float = 0.0
    mitre_technique: Optional[str] = None
    mitre_tactic: Optional[str] = None
    attack_path: List[str] = []
    impact_description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Patch Schemas
# ============================================================================


class PatchResponse(BaseModel):
    """Response model for code patch."""
    id: str
    scan_id: str
    finding_id: Optional[str] = None
    original_code: str
    patched_code: str
    explanation: Optional[str] = None
    is_ai_generated: bool = False
    confidence: float = 0.0
    can_auto_apply: bool = False
    apply_complexity: Optional[str] = None
    applied: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Report Schemas
# ============================================================================


class ReportResponse(BaseModel):
    """Response model for scan report."""
    id: str
    scan_id: str
    title: str
    summary: Optional[str] = None
    overall_risk_score: float = 0.0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    patch_coverage: float = 0.0
    remediation_effort: Optional[str] = None
    estimated_remediation_time: Optional[int] = None
    pdf_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReportDetailResponse(ReportResponse):
    """Extended report response with full data."""
    executive_summary: Optional[str] = None
    detailed_findings: List[Any] = []
    recommendations: List[str] = []
    json_data: dict = {}


# ============================================================================
# List Response Schemas
# ============================================================================


class PaginatedResponse(BaseModel):
    """Pagination metadata."""
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


class ScanListResponse(PaginatedResponse):
    """Response for scan list endpoint."""
    scans: List[ScanResponse] = []


class FindingListResponse(PaginatedResponse):
    """Response for finding list endpoint."""
    findings: List[FindingResponse] = []


class AttackListResponse(PaginatedResponse):
    """Response for attack list endpoint."""
    attacks: List[AttackResponse] = []


class PatchListResponse(PaginatedResponse):
    """Response for patch list endpoint."""
    patches: List[PatchResponse] = []


# ============================================================================
# Error Response Schema
# ============================================================================


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str = "An error occurred"
    error_code: str = "ERROR"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

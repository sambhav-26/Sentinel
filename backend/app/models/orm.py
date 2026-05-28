"""
SQLAlchemy ORM models for SentinelOS.

Defines database schema for:
- Users (account management)
- Repositories (code repositories to scan)
- Scans (vulnerability scans)
- Findings (discovered vulnerabilities)
- Attacks (simulated attack paths)
- Patches (code fixes)
- Reports (scan reports)
- Agent Logs (execution logs)
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    JSON,
    Enum,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship
import enum

# Base class for all models
Base = declarative_base()


class ScanStatus(str, enum.Enum):
    """Scan execution status."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SeverityLevel(str, enum.Enum):
    """Vulnerability severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class User(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    api_key = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    repositories = relationship("Repository", back_populates="user")
    scans = relationship("Scan", back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"


class Repository(Base):
    """Source code repository model."""
    __tablename__ = "repositories"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_repo_name"),
    )

    # Relationships
    user = relationship("User", back_populates="repositories")
    scans = relationship("Scan", back_populates="repository")

    def __repr__(self):
        return f"<Repository {self.name}>"


class Scan(Base):
    """Vulnerability scan execution model."""
    __tablename__ = "scans"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    repository_id = Column(String(36), ForeignKey("repositories.id"), nullable=False)
    
    status = Column(String(20), default=ScanStatus.QUEUED, nullable=False, index=True)
    progress = Column(Integer, default=0)  # 0-100
    
    total_files = Column(Integer, default=0)
    files_scanned = Column(Integer, default=0)
    
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    error_message = Column(Text, nullable=True)
    custom_metadata = Column(JSON, default={})  # Custom metadata
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="scans")
    repository = relationship("Repository", back_populates="scans")
    findings = relationship("Finding", back_populates="scan", cascade="all, delete-orphan")
    attacks = relationship("Attack", back_populates="scan", cascade="all, delete-orphan")
    patches = relationship("Patch", back_populates="scan", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="scan", cascade="all, delete-orphan")
    logs = relationship("AgentLog", back_populates="scan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Scan {self.id} - {self.status}>"


class Finding(Base):
    """Discovered vulnerability model."""
    __tablename__ = "findings"

    id = Column(String(36), primary_key=True)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False)
    
    vulnerability_type = Column(String(255), nullable=False)
    severity = Column(String(20), nullable=False)  # critical, high, medium, low, info
    
    file_path = Column(String(500), nullable=False)
    line_number = Column(Integer, nullable=False)
    column_number = Column(Integer, default=0)
    
    cwe_id = Column(String(20), nullable=True)  # CWE-89, CWE-79, etc.
    cwe_name = Column(String(255), nullable=True)
    
    owasp_category = Column(String(255), nullable=True)
    exploitability_score = Column(Float, default=0.0)
    
    code_snippet = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    
    is_ignored = Column(Boolean, default=False)
    ignore_reason = Column(Text, nullable=True)
    
    detection_source = Column(String(100), nullable=True)  # bandit, semgrep, custom
    confidence = Column(Float, default=1.0)  # 0-1
    
    custom_metadata = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    scan = relationship("Scan", back_populates="findings")
    attack = relationship("Attack", back_populates="finding", uselist=False)
    patch = relationship("Patch", back_populates="finding", uselist=False)

    def __repr__(self):
        return f"<Finding {self.id} - {self.vulnerability_type}>"


class Attack(Base):
    """Simulated attack path model."""
    __tablename__ = "attacks"

    id = Column(String(36), primary_key=True)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False)
    finding_id = Column(String(36), ForeignKey("findings.id"), nullable=True)
    
    attack_type = Column(String(255), nullable=False)  # RCE, SQLi, XSS, etc.
    attack_vector = Column(String(255), nullable=True)
    success_probability = Column(Float, default=0.0)  # 0-1
    
    impact_score = Column(Float, default=0.0)
    mitre_technique = Column(String(20), nullable=True)  # T1059, T1190, etc.
    mitre_tactic = Column(String(100), nullable=True)  # Execution, Initial Access, etc.
    
    attack_path = Column(JSON, default=[])  # List of attack steps
    impact_description = Column(Text, nullable=True)
    
    prerequisites = Column(JSON, default=[])  # What must be true for attack to work
    mitigation = Column(Text, nullable=True)
    
    custom_metadata = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    scan = relationship("Scan", back_populates="attacks")
    finding = relationship("Finding", back_populates="attack")

    def __repr__(self):
        return f"<Attack {self.id} - {self.attack_type}>"


class Patch(Base):
    """Code patch/fix model."""
    __tablename__ = "patches"

    id = Column(String(36), primary_key=True)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False)
    finding_id = Column(String(36), ForeignKey("findings.id"), nullable=True)
    
    original_code = Column(Text, nullable=False)
    patched_code = Column(Text, nullable=False)
    
    explanation = Column(Text, nullable=True)  # Why this patch fixes the issue
    additional_context = Column(Text, nullable=True)
    
    is_ai_generated = Column(Boolean, default=False)
    confidence = Column(Float, default=0.0)  # How confident in this patch
    
    can_auto_apply = Column(Boolean, default=False)
    apply_complexity = Column(String(50), nullable=True)  # simple, moderate, complex
    
    applied = Column(Boolean, default=False)
    applied_at = Column(DateTime, nullable=True)
    
    custom_metadata = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    scan = relationship("Scan", back_populates="patches")
    finding = relationship("Finding", back_populates="patch")

    def __repr__(self):
        return f"<Patch {self.id}>"


class Report(Base):
    """Scan report model."""
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    
    # Risk metrics
    overall_risk_score = Column(Float, default=0.0)  # 0-100
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    
    # Remediation
    patch_coverage = Column(Float, default=0.0)  # % of findings with patches
    remediation_effort = Column(String(50), nullable=True)  # low, medium, high
    estimated_remediation_time = Column(Integer, nullable=True)  # minutes
    
    # File storage
    pdf_url = Column(String(500), nullable=True)
    json_data = Column(JSON, default={})
    
    executive_summary = Column(Text, nullable=True)
    detailed_findings = Column(JSON, default=[])
    recommendations = Column(JSON, default=[])
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    scan = relationship("Scan", back_populates="reports")

    def __repr__(self):
        return f"<Report {self.id}>"


class AgentLog(Base):
    """Agent execution log model."""
    __tablename__ = "agent_logs"

    id = Column(String(36), primary_key=True)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False)
    
    agent_name = Column(String(100), nullable=False)  # scanner, threat, attack, patch, report
    agent_step = Column(Integer, default=0)  # Agent step number
    
    log_level = Column(String(20), default="INFO")  # DEBUG, INFO, WARN, ERROR
    message = Column(Text, nullable=False)
    
    details = Column(JSON, default={})  # Structured data
    
    execution_time_ms = Column(Integer, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    scan = relationship("Scan", back_populates="logs")

    def __repr__(self):
        return f"<AgentLog {self.agent_name} - {self.log_level}>"

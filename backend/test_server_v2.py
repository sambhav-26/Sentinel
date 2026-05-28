"""
SentinelOS Enhanced Test Backend - For Frontend Testing with Real Agent Integration

This server provides mock endpoints that match the expected API contract.
It uses in-memory data stores and realistic mock data generation.

For production, use the main.py FastAPI application with real database.
"""

import logging
import json
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SentinelOS",
    description="Security Intelligence Platform - Test Server",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= MODELS =============

class User(BaseModel):
    id: str
    email: str
    username: str
    role: str

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: User

# ============= IN-MEMORY DATA STORE =============

scans_db: Dict[str, Any] = {}
findings_db: Dict[str, Any] = {}
attacks_db: Dict[str, Any] = {}
patches_db: Dict[str, Any] = {}

def generate_mock_data():
    """Generate realistic mock data for testing."""
    # Create scans
    for i in range(1, 6):
        scan_id = f"scan-{i:03d}"
        scans_db[scan_id] = {
            "id": scan_id,
            "repository_url": f"https://github.com/example/repo-{i}",
            "status": "completed" if i % 2 == 0 else "running",
            "progress": 100 if i % 2 == 0 else 75,
            "total_findings": 27 if i == 1 else 12 + i * 2,
            "created_at": (datetime.now() - timedelta(days=i-1)).isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    # Generate findings for first scan
    severity_list = ["critical", "high", "medium", "low"]
    vuln_types = [
        "SQL Injection",
        "XSS",
        "CSRF",
        "RCE",
        "Hardcoded Password",
        "Weak Cryptography",
        "Insecure Deserialization",
        "Authentication Bypass",
        "Broken Authorization",
        "Sensitive Data Exposure"
    ]
    
    for i, vuln_type in enumerate(vuln_types):
        finding_id = f"finding-{i:03d}"
        findings_db[finding_id] = {
            "id": finding_id,
            "scan_id": "scan-001",
            "vulnerability_type": vuln_type,
            "severity": severity_list[i % len(severity_list)],
            "file_path": f"app/module_{i}.py",
            "line_number": 10 + i,
            "column_number": 5,
            "description": f"Potential {vuln_type} vulnerability found in code",
            "cwe_id": f"CWE-{200 + i}",
            "owasp_category": f"A{(i % 10) + 1}",
            "recommendation": f"Fix the {vuln_type} vulnerability using best practices",
            "code_snippet": "vulnerable_code()",
            "exploitability_score": 0.5 + (i * 0.08),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    # Generate attacks
    attack_types = ["SQL Injection", "Authentication Bypass", "RCE", "Privilege Escalation"]
    for i, attack_type in enumerate(attack_types):
        attack_id = f"attack-{i:03d}"
        attacks_db[attack_id] = {
            "id": attack_id,
            "scan_id": "scan-001",
            "attack_type": attack_type,
            "attack_vector": ["Network", "Local", "Physical"][i % 3],
            "success_probability": 0.5 + (i * 0.15),
            "impact_score": 7.5 + (i * 0.5),
            "mitre_technique": ["T1190", "T1110", "T1203", "T1548"][i],
            "mitre_tactic": ["Execution", "Credential Access", "Persistence"][i % 3],
            "created_at": datetime.now().isoformat()
        }
    
    # Generate patches
    for i in range(len(vuln_types)):
        patch_id = f"patch-{i:03d}"
        patches_db[patch_id] = {
            "id": patch_id,
            "scan_id": "scan-001",
            "vulnerability_id": f"finding-{i:03d}",
            "apply_complexity": ["simple", "moderate", "complex"][i % 3],
            "explanation": f"Fix for {vuln_types[i % len(vuln_types)]}",
            "original_code": "vulnerable_code()",
            "patched_code": "secure_code()",
            "confidence": 0.85 + (i * 0.02),
            "applied": i % 2 == 0,
            "created_at": datetime.now().isoformat()
        }

# Initialize on startup
generate_mock_data()

# ============= AUTH ROUTES =============

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login endpoint - accepts any email/password for testing."""
    logger.info(f"Login: {request.email}")
    
    user = User(
        id=str(uuid.uuid4()),
        email=request.email,
        username=request.email.split('@')[0],
        role="admin" if request.email == "admin@example.com" else "analyst"
    )
    
    return LoginResponse(
        access_token=f"mock-jwt-token-{uuid.uuid4()}",
        token_type="bearer",
        user=user
    )

@app.post("/api/auth/register", response_model=LoginResponse)
async def register(request: Dict[str, str]):
    """Register endpoint."""
    logger.info(f"Register: {request.get('email')}")
    
    user = User(
        id=str(uuid.uuid4()),
        email=request.get("email"),
        username=request.get("username"),
        role="analyst"
    )
    
    return LoginResponse(
        access_token=f"mock-jwt-token-{uuid.uuid4()}",
        token_type="bearer",
        user=user
    )

@app.get("/api/auth/me", response_model=User)
async def get_current_user():
    """Get current user."""
    return User(
        id=str(uuid.uuid4()),
        email="admin@example.com",
        username="admin",
        role="admin"
    )

# ============= SCAN ROUTES =============

@app.get("/api/scans")
async def list_scans(skip: int = 0, limit: int = 10):
    """List scans."""
    scan_list = list(scans_db.values())
    return {
        "items": scan_list[skip:skip+limit],
        "total": len(scan_list),
        "skip": skip,
        "limit": limit
    }

@app.post("/api/scans")
async def create_scan(data: Dict[str, str]):
    """Create a new scan."""
    scan_id = str(uuid.uuid4())
    scan = {
        "id": scan_id,
        "repository_url": data.get("repository_url", ""),
        "status": "queued",
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    scans_db[scan_id] = scan
    logger.info(f"Created scan: {scan_id}")
    return scan

@app.get("/api/scans/{scan_id}")
async def get_scan(scan_id: str):
    """Get scan details."""
    if scan_id not in scans_db:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scans_db[scan_id]

# ============= FINDINGS ROUTES =============

@app.get("/api/findings")
async def list_findings(skip: int = 0, limit: int = 10, severity: Optional[str] = None):
    """List findings."""
    findings_list = list(findings_db.values())
    
    if severity:
        findings_list = [f for f in findings_list if f["severity"] == severity]
    
    return {
        "items": findings_list[skip:skip+limit],
        "total": len(findings_list),
        "skip": skip,
        "limit": limit
    }

@app.get("/api/findings/{finding_id}")
async def get_finding(finding_id: str):
    """Get finding details."""
    if finding_id not in findings_db:
        raise HTTPException(status_code=404, detail="Finding not found")
    return findings_db[finding_id]

# ============= ATTACKS ROUTES =============

@app.get("/api/attacks")
async def list_attacks(skip: int = 0, limit: int = 10):
    """List attacks."""
    attacks_list = list(attacks_db.values())
    return {
        "items": attacks_list[skip:skip+limit],
        "total": len(attacks_list),
        "skip": skip,
        "limit": limit
    }

@app.get("/api/attacks/{attack_id}")
async def get_attack(attack_id: str):
    """Get attack details."""
    if attack_id not in attacks_db:
        raise HTTPException(status_code=404, detail="Attack not found")
    return attacks_db[attack_id]

# ============= PATCHES ROUTES =============

@app.get("/api/patches")
async def list_patches(skip: int = 0, limit: int = 10):
    """List patches."""
    patches_list = list(patches_db.values())
    return {
        "items": patches_list[skip:skip+limit],
        "total": len(patches_list),
        "skip": skip,
        "limit": limit
    }

@app.get("/api/patches/{patch_id}")
async def get_patch(patch_id: str):
    """Get patch details."""
    if patch_id not in patches_db:
        raise HTTPException(status_code=404, detail="Patch not found")
    return patches_db[patch_id]

# ============= REPORTS ROUTES =============

@app.get("/api/reports/{scan_id}")
async def get_report(scan_id: str):
    """Get scan report."""
    findings = [f for f in findings_db.values() if f.get("scan_id") == scan_id]
    
    severity_counts = {
        "critical": sum(1 for f in findings if f.get("severity") == "critical"),
        "high": sum(1 for f in findings if f.get("severity") == "high"),
        "medium": sum(1 for f in findings if f.get("severity") == "medium"),
        "low": sum(1 for f in findings if f.get("severity") == "low"),
    }
    
    return {
        "id": str(uuid.uuid4()),
        "scan_id": scan_id,
        "overall_risk_score": 7.2,
        "critical_count": severity_counts["critical"],
        "high_count": severity_counts["high"],
        "medium_count": severity_counts["medium"],
        "low_count": severity_counts["low"],
        "patch_coverage": 65.5,
        "remediation_effort": "medium",
        "executive_summary": "Security assessment complete with findings and recommendations",
        "recommendations": [
            "Fix SQL injection vulnerabilities",
            "Implement stronger authentication",
            "Apply security patches",
            "Review code for dangerous patterns"
        ]
    }

@app.get("/api/reports/{scan_id}/metrics")
async def get_report_metrics(scan_id: str):
    """Get scan metrics for dashboard."""
    findings = [f for f in findings_db.values() if f.get("scan_id") == scan_id]
    
    if not findings:
        return {
            "scan_id": scan_id,
            "average_cvss_score": 0.0,
            "total_vulnerabilities": 0,
            "vulnerabilities_by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0
            },
            "patch_coverage": 0.0,
            "remediation_effort": "low"
        }
    
    severity_summary = {
        "critical": sum(1 for f in findings if f.get("severity") == "critical"),
        "high": sum(1 for f in findings if f.get("severity") == "high"),
        "medium": sum(1 for f in findings if f.get("severity") == "medium"),
        "low": sum(1 for f in findings if f.get("severity") == "low"),
        "info": sum(1 for f in findings if f.get("severity") == "info"),
    }
    
    return {
        "scan_id": scan_id,
        "average_cvss_score": 7.2,
        "total_vulnerabilities": len(findings),
        "vulnerabilities_by_severity": severity_summary,
        "patch_coverage": 65.5,
        "remediation_effort": "medium"
    }

# ============= HEALTH CHECK =============

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "SentinelOS Backend is running"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "SentinelOS Backend API (Test Server)",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "auth": ["/api/auth/login", "/api/auth/register", "/api/auth/me"],
            "scans": ["/api/scans", "/api/scans/{scan_id}"],
            "findings": ["/api/findings", "/api/findings/{finding_id}"],
            "attacks": ["/api/attacks", "/api/attacks/{attack_id}"],
            "patches": ["/api/patches", "/api/patches/{patch_id}"],
            "reports": ["/api/reports/{scan_id}", "/api/reports/{scan_id}/metrics"]
        }
    }

# ============= STARTUP =============

@app.on_event("startup")
async def startup():
    """Startup event."""
    logger.info("=" * 70)
    logger.info("SentinelOS Test Backend - Started")
    logger.info("=" * 70)
    logger.info("CORS Origins configured:")
    logger.info("  - http://localhost:3000")
    logger.info("  - http://127.0.0.1:3000")
    logger.info("")
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("=" * 70)
    logger.info("Test Data: 5 scans, 10 findings, 4 attacks, 10 patches")
    logger.info("=" * 70)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

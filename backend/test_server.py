"""
SentinelOS Mock Backend - For testing frontend-backend connection
This is a simplified version that runs without a database.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SentinelOS",
    description="Security Intelligence Platform",
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

class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str

class Scan(BaseModel):
    id: str
    repository_url: str
    status: str
    progress: int
    created_at: str

class Finding(BaseModel):
    id: str
    scan_id: str
    vulnerability_type: str
    severity: str
    description: str

# ============= AUTH ROUTES =============

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login endpoint - accepts any email/password for testing.
    Returns a mock JWT token and user data.
    """
    logger.info(f"Login attempt: {request.email}")
    
    # Mock authentication - accept demo credentials
    user = User(
        id=str(uuid.uuid4()),
        email=request.email,
        username=request.email.split('@')[0],
        role="admin" if request.email == "admin@example.com" else "analyst"
    )
    
    # Return mock response
    return LoginResponse(
        access_token=f"mock-jwt-token-{uuid.uuid4()}",
        token_type="bearer",
        user=user
    )

@app.post("/api/auth/register", response_model=LoginResponse)
async def register(request: RegisterRequest):
    """
    Register endpoint - creates new user for testing.
    """
    logger.info(f"Register attempt: {request.email}")
    
    user = User(
        id=str(uuid.uuid4()),
        email=request.email,
        username=request.username,
        role="analyst"
    )
    
    return LoginResponse(
        access_token=f"mock-jwt-token-{uuid.uuid4()}",
        token_type="bearer",
        user=user
    )

@app.get("/api/auth/me", response_model=User)
async def get_current_user():
    """
    Get current user endpoint.
    """
    return User(
        id=str(uuid.uuid4()),
        email="admin@example.com",
        username="admin",
        role="admin"
    )

# ============= SCAN ROUTES =============

@app.get("/api/scans")
async def list_scans(skip: int = 0, limit: int = 10):
    """
    List scans with mock data.
    """
    mock_scans = [
        Scan(
            id=f"scan-{i:03d}",
            repository_url=f"https://github.com/example/repo-{i}",
            status="completed" if i % 2 == 0 else "running",
            progress=100 if i % 2 == 0 else 75,
            created_at=(datetime.now() - timedelta(days=i)).isoformat()
        )
        for i in range(1, 6)
    ]
    return {
        "items": mock_scans[skip:skip+limit],
        "total": len(mock_scans),
        "skip": skip,
        "limit": limit
    }

@app.post("/api/scans")
async def create_scan(repository_url: dict):
    """
    Create a new scan.
    """
    scan = Scan(
        id=str(uuid.uuid4()),
        repository_url=repository_url.get("repository_url", ""),
        status="queued",
        progress=0,
        created_at=datetime.now().isoformat()
    )
    logger.info(f"Created scan: {scan.id}")
    return scan

@app.get("/api/scans/{scan_id}")
async def get_scan(scan_id: str):
    """
    Get scan details.
    """
    return Scan(
        id=scan_id,
        repository_url="https://github.com/example/test",
        status="running",
        progress=45,
        created_at=datetime.now().isoformat()
    )

# ============= FINDINGS ROUTES =============

@app.get("/api/findings")
async def list_findings(skip: int = 0, limit: int = 10):
    """
    List security findings with mock data.
    """
    severities = ["critical", "high", "medium", "low"]
    findings = [
        Finding(
            id=f"finding-{i:03d}",
            scan_id="scan-001",
            vulnerability_type=["SQL Injection", "XSS", "CSRF", "RCE"][i % 4],
            severity=severities[i % 4],
            description=f"Mock vulnerability #{i}"
        )
        for i in range(1, 11)
    ]
    return {
        "items": findings[skip:skip+limit],
        "total": len(findings),
        "skip": skip,
        "limit": limit
    }

# ============= ATTACKS ROUTES =============

@app.get("/api/attacks")
async def list_attacks(skip: int = 0, limit: int = 10):
    """
    List attack scenarios with mock data.
    """
    attacks = [
        {
            "id": f"attack-{i:03d}",
            "attack_type": ["SQL Injection", "Authentication Bypass", "RCE"][i % 3],
            "attack_vector": ["Network", "Local", "Physical"][i % 3],
            "success_probability": 0.5 + (i * 0.1),
            "impact_score": 7.5 + (i * 0.5),
            "mitre_tactic": ["T1190", "T1566", "T1005"][i % 3]
        }
        for i in range(1, 6)
    ]
    return {
        "items": attacks[skip:skip+limit],
        "total": len(attacks),
        "skip": skip,
        "limit": limit
    }

# ============= PATCHES ROUTES =============

@app.get("/api/patches")
async def list_patches(skip: int = 0, limit: int = 10):
    """
    List code patches with mock data.
    """
    patches = [
        {
            "id": f"patch-{i:03d}",
            "vulnerability_id": f"finding-{i:03d}",
            "apply_complexity": ["simple", "moderate", "complex"][i % 3],
            "explanation": f"Fix vulnerability #{i}",
            "original_code": "vulnerable_code()",
            "patched_code": "secure_code()",
            "confidence": 0.85 + (i * 0.05),
            "applied": i % 2 == 0
        }
        for i in range(1, 6)
    ]
    return {
        "items": patches[skip:skip+limit],
        "total": len(patches),
        "skip": skip,
        "limit": limit
    }

# ============= REPORTS ROUTES =============

@app.get("/api/reports/{scan_id}")
async def get_report(scan_id: str):
    """
    Get scan report with mock data.
    """
    return {
        "id": str(uuid.uuid4()),
        "scan_id": scan_id,
        "overall_risk_score": 7.2,
        "critical_count": 2,
        "high_count": 5,
        "medium_count": 8,
        "low_count": 12,
        "patch_coverage": 65.5,
        "remediation_effort": "medium",
        "executive_summary": "Mock security assessment report",
        "recommendations": [
            "Fix SQL injection vulnerabilities",
            "Implement authentication bypass protections",
            "Apply security patches"
        ]
    }

@app.get("/api/reports/{scan_id}/metrics")
async def get_report_metrics(scan_id: str):
    """
    Get scan report metrics.
    """
    return {
        "scan_id": scan_id,
        "average_cvss_score": 7.2,
        "total_vulnerabilities": 27,
        "vulnerabilities_by_severity": {
            "critical": 2,
            "high": 5,
            "medium": 8,
            "low": 12
        },
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
        "message": "SentinelOS Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# ============= STARTUP =============

@app.on_event("startup")
async def startup():
    """Startup event."""
    logger.info("=" * 60)
    logger.info("SentinelOS Backend Started")
    logger.info("=" * 60)
    logger.info("Frontend CORS Origins configured:")
    logger.info("  - http://localhost:3000")
    logger.info("  - http://127.0.0.1:3000")
    logger.info("")
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("=" * 60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
API routes aggregation.

Imports all route modules and creates a combined router.
This is included in main.py to register all endpoints.
"""

from fastapi import APIRouter

from app.api import scans, findings, attacks, patches, reports

# Create main API router
router = APIRouter(prefix="/api")

# Include all sub-routers
router.include_router(scans.router, prefix="/scans", tags=["scans"])
router.include_router(findings.router, prefix="/findings", tags=["findings"])
router.include_router(attacks.router, prefix="/attacks", tags=["attacks"])
router.include_router(patches.router, prefix="/patches", tags=["patches"])
router.include_router(reports.router, prefix="/reports", tags=["reports"])

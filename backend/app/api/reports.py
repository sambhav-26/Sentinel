"""Report generation and export routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
from datetime import datetime
import csv
from io import StringIO

from app.models.database import get_db
from app.models import Report, Scan
from app.schemas import ReportDetailResponse

router = APIRouter()


@router.get("/{scan_id}", response_model=ReportDetailResponse)
async def get_report(
    scan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get scan report."""
    # Check scan exists
    scan = await db.get(Scan, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Get or create report
    query = select(Report).where(Report.scan_id == scan_id)
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not yet generated")
    
    return ReportDetailResponse.from_orm(report)


@router.post("/{scan_id}/export")
async def export_report(
    scan_id: str,
    format: str = Query("json", regex="^(json|csv)$"),
    db: AsyncSession = Depends(get_db)
):
    """Export report as JSON or CSV.
    
    Note: PDF export would require additional libraries (reportlab, weasyprint).
    For now, supporting JSON and CSV exports.
    """
    # Check scan exists
    scan = await db.get(Scan, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Get report
    query = select(Report).where(Report.scan_id == scan_id)
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not yet generated")
    
    if format == "json":
        # Return JSON export
        export_data = {
            "scan_id": scan_id,
            "title": report.title,
            "summary": report.summary,
            "overall_risk_score": report.overall_risk_score,
            "critical_count": report.critical_count,
            "high_count": report.high_count,
            "medium_count": report.medium_count,
            "low_count": report.low_count,
            "patch_coverage": report.patch_coverage,
            "remediation_effort": report.remediation_effort,
            "executive_summary": report.executive_summary,
            "detailed_findings": report.detailed_findings or [],
            "recommendations": report.recommendations or [],
            "generated_at": report.created_at.isoformat(),
        }
        
        return JSONResponse(
            content=export_data,
            headers={
                "Content-Disposition": f"attachment; filename=report_{scan_id}.json"
            }
        )
    
    elif format == "csv":
        # Generate CSV export
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        
        # Write header
        writer.writerow(["Metric", "Value"])
        
        # Write data
        writer.writerow(["Scan ID", scan_id])
        writer.writerow(["Title", report.title])
        writer.writerow(["Overall Risk Score", report.overall_risk_score])
        writer.writerow(["Critical Findings", report.critical_count])
        writer.writerow(["High Findings", report.high_count])
        writer.writerow(["Medium Findings", report.medium_count])
        writer.writerow(["Low Findings", report.low_count])
        writer.writerow(["Patch Coverage", f"{report.patch_coverage}%"])
        writer.writerow(["Remediation Effort", report.remediation_effort])
        writer.writerow(["Generated", report.created_at.isoformat()])
        
        return JSONResponse(
            content={"csv": csv_buffer.getvalue()},
            headers={
                "Content-Disposition": f"attachment; filename=report_{scan_id}.csv"
            }
        )

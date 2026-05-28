/**
 * Report types - Security scan reports
 */

import { Timestamps, Metadata, PaginatedResponse } from './common';

/**
 * Report entity - Security scan report
 */
export interface Report extends Timestamps {
  id: string;
  scan_id: string;
  title: string;
  summary?: string;
  overall_risk_score: number; // 0-100
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  patch_coverage: number; // 0-100
  remediation_effort: 'low' | 'medium' | 'high';
  estimated_remediation_time?: number; // hours
  pdf_url?: string;
  json_data?: Metadata;
}

/**
 * Detailed report with full content
 */
export interface ReportDetail extends Report {
  executive_summary: string;
  detailed_findings: DetailedFinding[];
  recommendations: string[];
}

/**
 * Detailed finding in report
 */
export interface DetailedFinding {
  id: string;
  vulnerability: string;
  severity: string;
  file: string;
  line: number;
  cwe: string;
  description: string;
  recommendation: string;
  attack?: {
    type: string;
    probability: number;
    impact: number;
  };
  patch?: {
    id: string;
    confidence: number;
    complexity: string;
  };
}

/**
 * Report export options
 */
export type ReportExportFormat = 'json' | 'csv' | 'pdf' | 'markdown';

/**
 * Report export request
 */
export interface ExportReportRequest {
  report_id: string;
  format: ReportExportFormat;
}

/**
 * Report export response
 */
export interface ExportReportResponse {
  report_id: string;
  format: ReportExportFormat;
  url: string;
  file_name: string;
  size_bytes: number;
}

/**
 * Report summary for dashboard
 */
export interface ReportSummary {
  scan_id: string;
  title: string;
  generated_at: string;
  risk_score: number;
  risk_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'MINIMAL';
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  patch_coverage: number;
  remediation_effort: string;
}

/**
 * Report page for PDF
 */
export interface ReportPage {
  section: 'cover' | 'executive' | 'findings' | 'attacks' | 'patches' | 'recommendations';
  content: string;
  page_number: number;
}

/**
 * Report metrics
 */
export interface ReportMetrics {
  total_vulnerabilities: number;
  vulnerabilities_by_severity: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  vulnerabilities_by_type: {
    [key: string]: number;
  };
  average_cvss_score: number;
  security_posture_grade: 'A' | 'B' | 'C' | 'D' | 'F';
  remediation_priority: DetailedFinding[];
  quick_wins: DetailedFinding[];
}

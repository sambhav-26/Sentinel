/**
 * Report service - API operations for reports
 */

import apiClient from './api-client';
import {
  Report,
  ReportDetail,
  ReportSummary,
  ReportMetrics,
  ExportReportRequest,
  ExportReportResponse,
} from '@/types';

export class ReportService {
  /**
   * Get report for a scan
   */
  async getReport(scanId: string): Promise<ReportDetail> {
    return apiClient.get<ReportDetail>(`/reports/${scanId}`);
  }

  /**
   * Get report summary (lightweight version)
   */
  async getReportSummary(scanId: string): Promise<ReportSummary> {
    return apiClient.get<ReportSummary>(`/reports/${scanId}/summary`);
  }

  /**
   * Get report metrics
   */
  async getReportMetrics(scanId: string): Promise<ReportMetrics> {
    return apiClient.get<ReportMetrics>(`/reports/${scanId}/metrics`);
  }

  /**
   * Export report in various formats
   */
  async exportReport(
    scanId: string,
    format: 'json' | 'csv' | 'pdf' | 'markdown'
  ): Promise<ExportReportResponse> {
    return apiClient.post<ExportReportResponse>(
      `/reports/${scanId}/export`,
      { format }
    );
  }

  /**
   * Download report file (returns blob)
   */
  async downloadReportFile(
    scanId: string,
    format: 'json' | 'csv' | 'pdf' | 'markdown'
  ): Promise<Blob> {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
    const response = await fetch(
      `${apiUrl}/reports/${scanId}/download?format=${format}`
    );
    return response.blob();
  }

  /**
   * Get report as JSON (full object)
   */
  async getReportAsJson(scanId: string): Promise<string> {
    const response = await this.getReport(scanId);
    return JSON.stringify(response, null, 2);
  }

  /**
   * Send report via email
   */
  async emailReport(scanId: string, emailAddress: string): Promise<void> {
    return apiClient.post(`/reports/${scanId}/email`, { email: emailAddress });
  }

  /**
   * Compare two reports
   */
  async compareReports(
    scanId1: string,
    scanId2: string
  ): Promise<{
    findings_added: number;
    findings_removed: number;
    severity_change: number;
    risk_score_change: number;
  }> {
    return apiClient.get('/reports/compare', {
      params: { scan1: scanId1, scan2: scanId2 },
    });
  }

  /**
   * Get report templates
   */
  async getReportTemplates(): Promise<
    Array<{
      id: string;
      name: string;
      description: string;
      format: string;
    }>
  > {
    return apiClient.get('/reports/templates');
  }

  /**
   * Generate custom report
   */
  async generateCustomReport(
    scanId: string,
    templateId: string,
    options?: {
      include_findings?: boolean;
      include_attacks?: boolean;
      include_patches?: boolean;
      include_recommendations?: boolean;
    }
  ): Promise<ReportDetail> {
    return apiClient.post<ReportDetail>(
      `/reports/${scanId}/generate`,
      { templateId, ...options }
    );
  }
}

export default new ReportService();

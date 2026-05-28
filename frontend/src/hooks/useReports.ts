/**
 * useReports - Hook for report operations
 */

import { useState, useCallback } from 'react';
import { ReportDetail, ReportSummary, ReportMetrics, ExportReportResponse } from '@/types';
import { reportService } from '@/services';

interface UseReportsReturn {
  report: ReportDetail | null;
  summary: ReportSummary | null;
  metrics: ReportMetrics | null;
  loading: boolean;
  error: string | null;
  getReport: (scanId: string) => Promise<void>;
  getReportSummary: (scanId: string) => Promise<void>;
  getReportMetrics: (scanId: string) => Promise<void>;
  exportReport: (scanId: string, format: 'json' | 'csv' | 'pdf' | 'markdown') => Promise<void>;
  downloadReport: (scanId: string, format: 'json' | 'csv' | 'pdf' | 'markdown') => Promise<void>;
  emailReport: (scanId: string, email: string) => Promise<void>;
  compareReports: (
    scanId1: string,
    scanId2: string
  ) => Promise<{
    findings_added: number;
    findings_removed: number;
    severity_change: number;
    risk_score_change: number;
  }>;
}

export function useReports(): UseReportsReturn {
  const [report, setReport] = useState<ReportDetail | null>(null);
  const [summary, setSummary] = useState<ReportSummary | null>(null);
  const [metrics, setMetrics] = useState<ReportMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getReport = useCallback(async (scanId: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await reportService.getReport(scanId);
      setReport(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get report';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const getReportSummary = useCallback(async (scanId: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await reportService.getReportSummary(scanId);
      setSummary(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get report summary';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const getReportMetrics = useCallback(async (scanId: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await reportService.getReportMetrics(scanId);
      setMetrics(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get report metrics';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const exportReport = useCallback(
    async (scanId: string, format: 'json' | 'csv' | 'pdf' | 'markdown') => {
      setLoading(true);
      setError(null);
      try {
        await reportService.exportReport(scanId, format);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to export report';
        setError(message);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const downloadReport = useCallback(
    async (scanId: string, format: 'json' | 'csv' | 'pdf' | 'markdown') => {
      setError(null);
      try {
        const blob = await reportService.downloadReportFile(scanId, format);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `report-${scanId}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to download report';
        setError(message);
      }
    },
    []
  );

  const emailReport = useCallback(async (scanId: string, email: string) => {
    setError(null);
    try {
      await reportService.emailReport(scanId, email);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to email report';
      setError(message);
    }
  }, []);

  const compareReports = useCallback(
    async (scanId1: string, scanId2: string) => {
      setError(null);
      try {
        return await reportService.compareReports(scanId1, scanId2);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to compare reports';
        setError(message);
        throw err;
      }
    },
    []
  );

  return {
    report,
    summary,
    metrics,
    loading,
    error,
    getReport,
    getReportSummary,
    getReportMetrics,
    exportReport,
    downloadReport,
    emailReport,
    compareReports,
  };
}

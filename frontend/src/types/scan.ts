/**
 * Scan types - Vulnerability scan objects
 */

import { Timestamps, ScanStatus, Metadata, PaginatedResponse } from './common';

/**
 * Scan entity
 */
export interface Scan extends Timestamps {
  id: string;
  user_id: string;
  repository_id: string;
  status: ScanStatus;
  progress: number; // 0-100
  total_files: number;
  files_scanned: number;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  metadata?: Metadata;
}

/**
 * Scan with detailed findings information
 */
export interface ScanDetail extends Scan {
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  total_findings: number;
}

/**
 * List of scans
 */
export type ScanList = PaginatedResponse<Scan>;

/**
 * Request to create a new scan
 */
export interface ScanCreateRequest {
  repository_url: string;
  repository_name?: string;
  description?: string;
}

/**
 * Scan progress information for UI polling
 */
export interface ScanProgress {
  scan_id: string;
  progress: number; // 0-100
  status: ScanStatus;
  findings_count?: number;
  current_agent?: string;
  elapsed_time_ms?: number;
}

/**
 * Scan statistics
 */
export interface ScanStats {
  total_scans: number;
  completed_scans: number;
  failed_scans: number;
  total_findings: number;
  critical_count: number;
  high_count: number;
  average_risk_score: number;
}

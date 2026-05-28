/**
 * API response types - Standardized API responses
 */

import { Scan, ScanDetail, ScanList } from './scan';
import { Finding, FindingDetail, FindingList } from './finding';
import { Attack, AttackDetail, AttackList } from './attack';
import { Patch, PatchDetail, PatchList } from './patch';
import { Report, ReportDetail, ExportReportResponse } from './report';

/**
 * Generic paginated API response
 */
export interface PaginatedApiResponse<T> {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: T[];
}

/**
 * Scan endpoints response types
 */
export namespace ScanResponses {
  export type CreateScan = Scan;
  export type GetScan = ScanDetail;
  export type ListScans = ScanList;
  export type GetFindings = FindingList;
}

/**
 * Finding endpoints response types
 */
export namespace FindingResponses {
  export type ListFindings = FindingList;
  export type GetFinding = FindingDetail;
  export type IgnoreFinding = Finding;
}

/**
 * Attack endpoints response types
 */
export namespace AttackResponses {
  export type ListAttacks = AttackList;
  export type GetAttack = AttackDetail;
}

/**
 * Patch endpoints response types
 */
export namespace PatchResponses {
  export type ListPatches = PatchList;
  export type GetPatch = PatchDetail;
}

/**
 * Report endpoints response types
 */
export namespace ReportResponses {
  export type GetReport = ReportDetail;
  export type ExportReport = ExportReportResponse;
}

/**
 * Standard error response from API
 */
export interface ApiErrorResponse {
  detail: string;
  status?: number;
}

/**
 * Health check response
 */
export interface HealthCheckResponse {
  status: 'ok' | 'error';
  database: 'connected' | 'disconnected';
  version: string;
  timestamp: string;
}

/**
 * Agent status response
 */
export interface AgentStatusResponse {
  agent_name: string;
  status: 'idle' | 'running' | 'completed' | 'failed';
  progress: number;
  message: string;
  execution_time_ms?: number;
}

/**
 * Batch operation response
 */
export interface BatchOperationResponse<T> {
  total: number;
  succeeded: number;
  failed: number;
  results: (T | ApiErrorResponse)[];
}

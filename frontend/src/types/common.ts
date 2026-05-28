/**
 * Common types and utilities for the API
 */

/**
 * Pagination information
 */
export interface PaginatedResponse<T> {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: T[];
}

/**
 * API error response
 */
export interface ErrorResponse {
  detail: string;
  status_code?: number;
}

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  data?: T;
  error?: ErrorResponse;
  success: boolean;
}

/**
 * Severity levels for vulnerabilities
 */
export type SeverityLevel = 'critical' | 'high' | 'medium' | 'low' | 'info';

/**
 * Scan status values
 */
export type ScanStatus = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';

/**
 * Threat types
 */
export type ThreatType =
  | 'injection'
  | 'cryptography'
  | 'authentication'
  | 'dangerous_execution'
  | 'misconfiguration'
  | 'critical_vulnerability'
  | 'high_severity'
  | 'medium_severity'
  | 'low_severity';

/**
 * Common metadata structure
 */
export interface Metadata {
  [key: string]: any;
}

/**
 * Base timestamps
 */
export interface Timestamps {
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
}

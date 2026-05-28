/**
 * Finding types - Vulnerability findings
 */

import { Timestamps, SeverityLevel, Metadata, PaginatedResponse } from './common';

/**
 * Finding entity - Individual vulnerability
 */
export interface Finding extends Timestamps {
  id: string;
  scan_id: string;
  vulnerability_type: string;
  severity: SeverityLevel;
  file_path: string;
  line_number: number;
  column_number: number;
  cwe_id?: string;
  cwe_name?: string;
  owasp_category?: string;
  exploitability_score: number;
  code_snippet?: string;
  description?: string;
  recommendation?: string;
  is_ignored: boolean;
  ignore_reason?: string;
  detection_source: string;
  confidence: number; // 0-1
  metadata?: Metadata;
}

/**
 * Detailed finding with related data
 */
export interface FindingDetail extends Finding {
  attack?: {
    id: string;
    attack_type: string;
    success_probability: number;
    impact_score: number;
  };
  patch?: {
    id: string;
    confidence: number;
    complexity: string;
  };
}

/**
 * List of findings
 */
export type FindingList = PaginatedResponse<Finding>;

/**
 * Request to ignore a finding
 */
export interface IgnoreFindingRequest {
  ignore_reason: string;
}

/**
 * Finding summary grouped by severity
 */
export interface FindingSummary {
  critical: Finding[];
  high: Finding[];
  medium: Finding[];
  low: Finding[];
  info: Finding[];
}

/**
 * Finding statistics
 */
export interface FindingStats {
  total: number;
  by_severity: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  };
  by_type: {
    [key: string]: number;
  };
  ignored_count: number;
}

/**
 * Finding for display in vulnerabilities table
 */
export interface FindingTableRow {
  id: string;
  type: string;
  severity: SeverityLevel;
  file: string;
  line: number;
  cwe: string;
  exploitability: number;
  ignored: boolean;
  patch_available: boolean;
}

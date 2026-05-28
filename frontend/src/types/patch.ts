/**
 * Patch types - Code fix suggestions
 */

import { Timestamps, Metadata, PaginatedResponse } from './common';

/**
 * Patch entity - Code fix suggestion
 */
export interface Patch extends Timestamps {
  id: string;
  scan_id: string;
  finding_id?: string;
  original_code: string;
  patched_code: string;
  explanation?: string;
  additional_context?: string;
  is_ai_generated: boolean;
  confidence: number; // 0-1
  can_auto_apply: boolean;
  apply_complexity: 'simple' | 'moderate' | 'complex';
  applied: boolean;
  applied_at?: string;
  metadata?: Metadata;
}

/**
 * Patch with detailed information
 */
export interface PatchDetail extends Patch {
  finding_type?: string;
  finding_severity?: string;
  affected_files?: string[];
  estimated_time_minutes?: number;
}

/**
 * List of patches
 */
export type PatchList = PaginatedResponse<Patch>;

/**
 * Request to apply a patch
 */
export interface ApplyPatchRequest {
  patch_id: string;
  dry_run?: boolean;
}

/**
 * Result of applying a patch
 */
export interface ApplyPatchResult {
  patch_id: string;
  success: boolean;
  message: string;
  files_modified?: string[];
  error?: string;
}

/**
 * Patch statistics
 */
export interface PatchStats {
  total_patches: number;
  applied_patches: number;
  pending_patches: number;
  auto_applicable: number;
  coverage_percentage: number; // % of findings with patches
  average_complexity: string;
}

/**
 * Patch for code diff viewer
 */
export interface PatchDiff {
  id: string;
  file_path: string;
  original: string;
  patched: string;
  language?: string;
  lineMapping?: {
    [key: number]: number; // original line -> patched line
  };
}

/**
 * Batch patch operation
 */
export interface BatchPatchRequest {
  patch_ids: string[];
  include_complex?: boolean;
  dry_run?: boolean;
}

/**
 * Batch patch result
 */
export interface BatchPatchResult {
  total: number;
  succeeded: number;
  failed: number;
  results: ApplyPatchResult[];
}

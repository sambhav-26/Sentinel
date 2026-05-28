/**
 * Patch service - API operations for patches
 */

import apiClient from './api-client';
import {
  Patch,
  PatchDetail,
  PatchList,
  ApplyPatchRequest,
  ApplyPatchResult,
  BatchPatchRequest,
  BatchPatchResult,
} from '@/types';

export class PatchService {
  /**
   * Get all patches
   */
  async listPatches(
    skip: number = 0,
    limit: number = 50
  ): Promise<PatchList> {
    return apiClient.get<PatchList>('/patches', {
      params: { skip, limit },
    });
  }

  /**
   * Get patch by ID
   */
  async getPatch(patchId: string): Promise<PatchDetail> {
    return apiClient.get<PatchDetail>(`/patches/${patchId}`);
  }

  /**
   * Get patches for a finding
   */
  async getPatchesByFinding(findingId: string): Promise<PatchList> {
    return apiClient.get<PatchList>('/patches', {
      params: { finding_id: findingId },
    });
  }

  /**
   * Get patches for a scan
   */
  async getPatchesByScan(scanId: string): Promise<PatchList> {
    return apiClient.get<PatchList>('/patches', {
      params: { scan_id: scanId },
    });
  }

  /**
   * Get auto-applicable patches
   */
  async getAutoApplicablePatches(scanId: string): Promise<PatchList> {
    return apiClient.get<PatchList>('/patches', {
      params: { scan_id: scanId, can_auto_apply: true },
    });
  }

  /**
   * Apply a single patch
   */
  async applyPatch(request: ApplyPatchRequest): Promise<ApplyPatchResult> {
    return apiClient.post<ApplyPatchResult>(
      `/patches/${request.patch_id}/apply`,
      { dry_run: request.dry_run }
    );
  }

  /**
   * Apply multiple patches
   */
  async applyPatches(request: BatchPatchRequest): Promise<BatchPatchResult> {
    return apiClient.post<BatchPatchResult>('/patches/apply-batch', request);
  }

  /**
   * Get patch complexity for a scan
   */
  async getPatchComplexity(scanId: string): Promise<{
    simple: number;
    moderate: number;
    complex: number;
  }> {
    return apiClient.get('/patches/complexity', {
      params: { scan_id: scanId },
    });
  }

  /**
   * Get patch coverage for a scan
   */
  async getPatchCoverage(scanId: string): Promise<{
    total_findings: number;
    patched_findings: number;
    coverage_percentage: number;
  }> {
    return apiClient.get('/patches/coverage', {
      params: { scan_id: scanId },
    });
  }

  /**
   * Download patch diff
   */
  async getPatchDiff(patchId: string): Promise<string> {
    return apiClient.get<string>(`/patches/${patchId}/diff`);
  }

  /**
   * Export patches as code
   */
  async exportPatches(scanId: string): Promise<Blob> {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/patches/export?scan_id=${scanId}`
    );
    return response.blob();
  }
}

export default new PatchService();

/**
 * Finding service - API operations for findings
 */

import apiClient from './api-client';
import {
  Finding,
  FindingDetail,
  FindingList,
  IgnoreFindingRequest,
} from '@/types';

export class FindingService {
  /**
   * Get all findings
   */
  async listFindings(
    skip: number = 0,
    limit: number = 50
  ): Promise<FindingList> {
    return apiClient.get<FindingList>('/findings', {
      params: { skip, limit },
    });
  }

  /**
   * Get finding by ID
   */
  async getFinding(findingId: string): Promise<FindingDetail> {
    return apiClient.get<FindingDetail>(`/findings/${findingId}`);
  }

  /**
   * Ignore a finding (mark as false positive)
   */
  async ignoreFinding(
    findingId: string,
    request: IgnoreFindingRequest
  ): Promise<Finding> {
    return apiClient.post<Finding>(
      `/findings/${findingId}/ignore`,
      request
    );
  }

  /**
   * Unignore a finding
   */
  async unignoreFinding(findingId: string): Promise<Finding> {
    return apiClient.post<Finding>(`/findings/${findingId}/unignore`);
  }

  /**
   * Get findings by severity
   */
  async findingsBySeverity(severity: string): Promise<FindingList> {
    return apiClient.get<FindingList>('/findings', {
      params: { severity },
    });
  }

  /**
   * Search findings by keyword
   */
  async searchFindings(keyword: string): Promise<FindingList> {
    return apiClient.get<FindingList>('/findings/search', {
      params: { q: keyword },
    });
  }

  /**
   * Export findings as CSV
   */
  async exportFindings(scanId: string): Promise<Blob> {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/findings/export?scan_id=${scanId}`
    );
    return response.blob();
  }
}

export default new FindingService();

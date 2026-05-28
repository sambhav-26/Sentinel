/**
 * Scan service - API operations for scans
 */

import apiClient from './api-client';
import {
  Scan,
  ScanDetail,
  ScanList,
  ScanCreateRequest,
  ScanProgress,
  FindingList,
} from '@/types';

export class ScanService {
  /**
   * Create a new scan
   */
  async createScan(data: ScanCreateRequest): Promise<Scan> {
    return apiClient.post<Scan>('/scans', data);
  }

  /**
   * Get scan details
   */
  async getScan(scanId: string): Promise<ScanDetail> {
    return apiClient.get<ScanDetail>(`/scans/${scanId}`);
  }

  /**
   * List all scans with pagination
   */
  async listScans(
    skip: number = 0,
    limit: number = 10,
    status?: string
  ): Promise<ScanList> {
    return apiClient.get<ScanList>('/scans', {
      params: { skip, limit, status },
    });
  }

  /**
   * Get findings for a scan
   */
  async getFindings(
    scanId: string,
    skip: number = 0,
    limit: number = 50,
    severity?: string
  ): Promise<FindingList> {
    return apiClient.get<FindingList>(`/scans/${scanId}/findings`, {
      params: { skip, limit, severity },
    });
  }

  /**
   * Cancel a scan
   */
  async cancelScan(scanId: string): Promise<Scan> {
    return apiClient.post<Scan>(`/scans/${scanId}/cancel`);
  }

  /**
   * Delete a scan
   */
  async deleteScan(scanId: string): Promise<void> {
    return apiClient.delete<void>(`/scans/${scanId}`);
  }

  /**
   * Get scan progress (for real-time updates)
   */
  async getScanProgress(scanId: string): Promise<ScanProgress> {
    return apiClient.get<ScanProgress>(`/scans/${scanId}/progress`);
  }

  /**
   * Poll scan until completion
   */
  async waitForScanCompletion(
    scanId: string,
    pollInterval: number = 2000,
    maxWaitTime: number = 300000
  ): Promise<ScanDetail> {
    const startTime = Date.now();

    const poll = async (): Promise<ScanDetail> => {
      const scan = await this.getScan(scanId);

      if (scan.status === 'completed' || scan.status === 'failed') {
        return scan;
      }

      const elapsed = Date.now() - startTime;
      if (elapsed > maxWaitTime) {
        throw new Error(`Scan timeout after ${maxWaitTime}ms`);
      }

      await new Promise((resolve) => setTimeout(resolve, pollInterval));
      return poll();
    };

    return poll();
  }
}

export default new ScanService();

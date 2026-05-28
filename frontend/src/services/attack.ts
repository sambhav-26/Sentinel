/**
 * Attack service - API operations for attacks
 */

import apiClient from './api-client';
import {
  Attack,
  AttackDetail,
  AttackList,
  AttackChain,
} from '@/types';

export class AttackService {
  /**
   * Get all attacks
   */
  async listAttacks(
    skip: number = 0,
    limit: number = 50
  ): Promise<AttackList> {
    return apiClient.get<AttackList>('/attacks', {
      params: { skip, limit },
    });
  }

  /**
   * Get attack by ID
   */
  async getAttack(attackId: string): Promise<AttackDetail> {
    return apiClient.get<AttackDetail>(`/attacks/${attackId}`);
  }

  /**
   * Get attacks for a finding
   */
  async getAttacksByFinding(findingId: string): Promise<AttackList> {
    return apiClient.get<AttackList>('/attacks', {
      params: { finding_id: findingId },
    });
  }

  /**
   * Get attacks by scan
   */
  async getAttacksByScan(scanId: string): Promise<AttackList> {
    return apiClient.get<AttackList>('/attacks', {
      params: { scan_id: scanId },
    });
  }

  /**
   * Get attacks by MITRE tactic
   */
  async getAttacksByTactic(tactic: string): Promise<AttackList> {
    return apiClient.get<AttackList>('/attacks', {
      params: { tactic },
    });
  }

  /**
   * Get attack chains (related attacks)
   */
  async getAttackChains(scanId: string): Promise<AttackChain[]> {
    return apiClient.get<AttackChain[]>(`/scans/${scanId}/attack-chains`);
  }

  /**
   * Get high-impact attacks
   */
  async getHighImpactAttacks(
    minImpact: number = 7.0
  ): Promise<AttackList> {
    return apiClient.get<AttackList>('/attacks', {
      params: { min_impact: minImpact },
    });
  }

  /**
   * Get high-probability attacks
   */
  async getHighProbabilityAttacks(
    minProbability: number = 0.75
  ): Promise<AttackList> {
    return apiClient.get<AttackList>('/attacks', {
      params: { min_probability: minProbability },
    });
  }

  /**
   * Export attacks as CSV
   */
  async exportAttacks(scanId: string): Promise<Blob> {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/attacks/export?scan_id=${scanId}`
    );
    return response.blob();
  }
}

export default new AttackService();

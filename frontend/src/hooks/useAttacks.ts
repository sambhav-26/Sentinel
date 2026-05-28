/**
 * useAttacks - Hook for attack operations
 */

import { useState, useCallback } from 'react';
import { Attack, AttackDetail, AttackList, AttackChain } from '@/types';
import { attackService } from '@/services';

interface UseAttacksReturn {
  attacks: AttackDetail[];
  attack: AttackDetail | null;
  attackChains: AttackChain[];
  loading: boolean;
  error: string | null;
  listAttacks: (skip?: number, limit?: number) => Promise<void>;
  getAttack: (id: string) => Promise<void>;
  getAttacksByScan: (scanId: string) => Promise<void>;
  getAttacksByFinding: (findingId: string) => Promise<void>;
  getAttacksByTactic: (tactic: string) => Promise<void>;
  getAttackChains: (scanId: string) => Promise<void>;
  getHighImpactAttacks: () => Promise<void>;
  getHighProbabilityAttacks: () => Promise<void>;
}

export function useAttacks(): UseAttacksReturn {
  const [attacks, setAttacks] = useState<AttackDetail[]>([]);
  const [attack, setAttack] = useState<AttackDetail | null>(null);
  const [attackChains, setAttackChains] = useState<AttackChain[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const listAttacks = useCallback(
    async (skip: number = 0, limit: number = 50) => {
      setLoading(true);
      setError(null);
      try {
        const result = await attackService.listAttacks(skip, limit);
        setAttacks(result.items as AttackDetail[]);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to load attacks';
        setError(message);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getAttack = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await attackService.getAttack(id);
      setAttack(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get attack';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const getAttacksByScan = useCallback(async (scanId: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await attackService.getAttacksByScan(scanId);
      setAttacks(result.items as AttackDetail[]);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load attacks';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const getAttacksByFinding = useCallback(async (findingId: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await attackService.getAttacksByFinding(findingId);
      setAttacks(result.items as AttackDetail[]);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load attacks';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const getAttacksByTactic = useCallback(async (tactic: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await attackService.getAttacksByTactic(tactic);
      setAttacks(result.items as AttackDetail[]);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load attacks';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const getAttackChains = useCallback(async (scanId: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await attackService.getAttackChains(scanId);
      setAttackChains(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load attack chains';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const getHighImpactAttacks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await attackService.getHighImpactAttacks();
      setAttacks(result.items as AttackDetail[]);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load attacks';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const getHighProbabilityAttacks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await attackService.getHighProbabilityAttacks();
      setAttacks(result.items as AttackDetail[]);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load attacks';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    attacks,
    attack,
    attackChains,
    loading,
    error,
    listAttacks,
    getAttack,
    getAttacksByScan,
    getAttacksByFinding,
    getAttacksByTactic,
    getAttackChains,
    getHighImpactAttacks,
    getHighProbabilityAttacks,
  };
}

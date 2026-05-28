/**
 * useFindings - Hook for finding operations
 */

import { useState, useCallback } from 'react';
import { Finding, FindingDetail, FindingList } from '@/types';
import { findingService } from '@/services';

interface UseFindingsReturn {
  findings: FindingDetail[];
  finding: FindingDetail | null;
  loading: boolean;
  error: string | null;
  listFindings: (skip?: number, limit?: number) => Promise<void>;
  getFinding: (id: string) => Promise<void>;
  ignoreFinding: (id: string, reason: string) => Promise<void>;
  unignoreFinding: (id: string) => Promise<void>;
  searchFindings: (keyword: string) => Promise<void>;
  findingsBySeverity: (severity: string) => Promise<void>;
}

export function useFindings(): UseFindingsReturn {
  const [findings, setFindings] = useState<FindingDetail[]>([]);
  const [finding, setFinding] = useState<FindingDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const listFindings = useCallback(
    async (skip: number = 0, limit: number = 50) => {
      setLoading(true);
      setError(null);
      try {
        const result = await findingService.listFindings(skip, limit);
        setFindings(result.items as FindingDetail[]);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to load findings';
        setError(message);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getFinding = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await findingService.getFinding(id);
      setFinding(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get finding';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const ignoreFinding = useCallback(
    async (id: string, reason: string) => {
      setError(null);
      try {
        await findingService.ignoreFinding(id, { ignore_reason: reason });
        setFindings((prev) =>
          prev.map((f) => (f.id === id ? { ...f, is_ignored: true, ignore_reason: reason } : f))
        );
        if (finding?.id === id) {
          setFinding({ ...finding, is_ignored: true, ignore_reason: reason });
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to ignore finding';
        setError(message);
      }
    },
    [finding]
  );

  const unignoreFinding = useCallback(async (id: string) => {
    setError(null);
    try {
      await findingService.unignoreFinding(id);
      setFindings((prev) =>
        prev.map((f) => (f.id === id ? { ...f, is_ignored: false } : f))
      );
      if (finding?.id === id) {
        setFinding({ ...finding, is_ignored: false });
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to unignore finding';
      setError(message);
    }
  }, [finding]);

  const searchFindings = useCallback(async (keyword: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await findingService.searchFindings(keyword);
      setFindings(result.items as FindingDetail[]);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Search failed';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const findingsBySeverity = useCallback(async (severity: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await findingService.findingsBySeverity(severity);
      setFindings(result.items as FindingDetail[]);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Filter failed';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    findings,
    finding,
    loading,
    error,
    listFindings,
    getFinding,
    ignoreFinding,
    unignoreFinding,
    searchFindings,
    findingsBySeverity,
  };
}

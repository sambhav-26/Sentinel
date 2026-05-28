/**
 * useScans - Hook for scan operations
 */

import { useState, useCallback } from 'react';
import { Scan, ScanDetail, ScanCreateRequest, ScanProgress } from '@/types';
import { scanService } from '@/services';

interface UseScanReturn {
  scan: ScanDetail | null;
  scans: Scan[];
  loading: boolean;
  error: string | null;
  createScan: (data: ScanCreateRequest) => Promise<Scan>;
  getScan: (id: string) => Promise<void>;
  listScans: (skip?: number, limit?: number) => Promise<void>;
  cancelScan: (id: string) => Promise<void>;
  deleteScan: (id: string) => Promise<void>;
  waitForCompletion: (id: string) => Promise<void>;
  getScanProgress: (id: string) => Promise<ScanProgress>;
}

export function useScans(): UseScanReturn {
  const [scan, setScan] = useState<ScanDetail | null>(null);
  const [scans, setScans] = useState<Scan[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createScan = useCallback(
    async (data: ScanCreateRequest): Promise<Scan> => {
      setLoading(true);
      setError(null);
      try {
        const result = await scanService.createScan(data);
        return result;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to create scan';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getScan = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await scanService.getScan(id);
      setScan(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get scan';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const listScans = useCallback(
    async (skip: number = 0, limit: number = 10) => {
      setLoading(true);
      setError(null);
      try {
        const result = await scanService.listScans(skip, limit);
        setScans(result.items);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to list scans';
        setError(message);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const cancelScan = useCallback(async (id: string) => {
    setError(null);
    try {
      const result = await scanService.cancelScan(id);
      setScan((prev) => (prev?.id === id ? { ...prev, status: result.status } : prev));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to cancel scan';
      setError(message);
    }
  }, []);

  const deleteScan = useCallback(async (id: string) => {
    setError(null);
    try {
      await scanService.deleteScan(id);
      setScans((prev) => prev.filter((s) => s.id !== id));
      if (scan?.id === id) setScan(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete scan';
      setError(message);
    }
  }, [scan?.id]);

  const waitForCompletion = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await scanService.waitForScanCompletion(id);
      setScan(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Scan failed or timed out';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getScanProgress = useCallback(
    async (id: string): Promise<ScanProgress> => {
      return scanService.getScanProgress(id);
    },
    []
  );

  return {
    scan,
    scans,
    loading,
    error,
    createScan,
    getScan,
    listScans,
    cancelScan,
    deleteScan,
    waitForCompletion,
    getScanProgress,
  };
}

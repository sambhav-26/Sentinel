/**
 * usePatches - Hook for patch operations
 */

import { useState, useCallback } from 'react';
import { Patch, PatchDetail, PatchList, ApplyPatchResult } from '@/types';
import { patchService } from '@/services';

interface UsePatchesReturn {
  patches: PatchDetail[];
  patch: PatchDetail | null;
  loading: boolean;
  error: string | null;
  listPatches: (skip?: number, limit?: number) => Promise<void>;
  getPatch: (id: string) => Promise<void>;
  getPatchesByScan: (scanId: string) => Promise<void>;
  getPatchesByFinding: (findingId: string) => Promise<void>;
  getAutoApplicablePatches: (scanId: string) => Promise<void>;
  applyPatch: (patchId: string, dryRun?: boolean) => Promise<ApplyPatchResult>;
  getPatchCoverage: (scanId: string) => Promise<void>;
}

export function usePatches(): UsePatchesReturn {
  const [patches, setPatches] = useState<PatchDetail[]>([]);
  const [patch, setPatch] = useState<PatchDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const listPatches = useCallback(
    async (skip: number = 0, limit: number = 50) => {
      setLoading(true);
      setError(null);
      try {
        const result = await patchService.listPatches(skip, limit);
        setPatches(result.items as PatchDetail[]);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to load patches';
        setError(message);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getPatch = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await patchService.getPatch(id);
      setPatch(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get patch';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const getPatchesByScan = useCallback(async (scanId: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await patchService.getPatchesByScan(scanId);
      setPatches(result.items as PatchDetail[]);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load patches';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const getPatchesByFinding = useCallback(async (findingId: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await patchService.getPatchesByFinding(findingId);
      setPatches(result.items as PatchDetail[]);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load patches';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const getAutoApplicablePatches = useCallback(async (scanId: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await patchService.getAutoApplicablePatches(scanId);
      setPatches(result.items as PatchDetail[]);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load patches';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const applyPatch = useCallback(
    async (patchId: string, dryRun: boolean = true): Promise<ApplyPatchResult> => {
      setError(null);
      try {
        const result = await patchService.applyPatch({ patch_id: patchId, dry_run: dryRun });
        if (result.success) {
          setPatches((prev) =>
            prev.map((p) => (p.id === patchId ? { ...p, applied: true } : p))
          );
        }
        return result;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to apply patch';
        setError(message);
        throw err;
      }
    },
    []
  );

  const getPatchCoverage = useCallback(async (scanId: string) => {
    setError(null);
    try {
      await patchService.getPatchCoverage(scanId);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get patch coverage';
      setError(message);
    }
  }, []);

  return {
    patches,
    patch,
    loading,
    error,
    listPatches,
    getPatch,
    getPatchesByScan,
    getPatchesByFinding,
    getAutoApplicablePatches,
    applyPatch,
    getPatchCoverage,
  };
}

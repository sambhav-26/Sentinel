'use client';

import { useEffect, useState } from 'react';
import { usePatches } from '@/hooks/usePatches';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Patch } from '@/types';

function PatchesContent() {
  const { patches, listPatches, applyPatch, loading, error } = usePatches();
  const [filterComplexity, setFilterComplexity] = useState<'all' | 'simple' | 'moderate' | 'complex'>('all');
  const [applyingId, setApplyingId] = useState<string | null>(null);

  useEffect(() => {
    listPatches(0, 100);
  }, []);

  const filtered = filterComplexity === 'all'
    ? patches
    : patches.filter(p => p.apply_complexity === filterComplexity);

  const complexityColors = {
    simple: 'bg-green-900 text-green-200',
    moderate: 'bg-yellow-900 text-yellow-200',
    complex: 'bg-red-900 text-red-200',
  };

  const handleApplyPatch = async (patchId: string) => {
    setApplyingId(patchId);
    try {
      await applyPatch(patchId, false);
    } catch (err) {
      console.error('Failed to apply patch:', err);
    } finally {
      setApplyingId(null);
    }
  };

  const stats = {
    total: patches.length,
    applied: patches.filter(p => p.applied).length,
    simple: patches.filter(p => p.apply_complexity === 'simple').length,
    moderate: patches.filter(p => p.apply_complexity === 'moderate').length,
    complex: patches.filter(p => p.apply_complexity === 'complex').length,
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Code Patches</h1>
        <p className="text-[var(--text-secondary)] mt-1">
          Suggested code fixes for discovered vulnerabilities
        </p>
      </div>

      <div className="grid grid-cols-4 gap-3">
        <div className="bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg p-4">
          <p className="text-sm text-[var(--text-secondary)]">Total Patches</p>
          <p className="text-2xl font-semibold mt-1">{stats.total}</p>
        </div>
        <div className="bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg p-4">
          <p className="text-sm text-[var(--text-secondary)]">Applied</p>
          <p className="text-2xl font-semibold mt-1 text-green-400">{stats.applied}</p>
        </div>
        <div className="bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg p-4">
          <p className="text-sm text-[var(--text-secondary)]">Coverage</p>
          <p className="text-2xl font-semibold mt-1">{stats.total > 0 ? ((stats.applied / stats.total) * 100).toFixed(0) : '0'}%</p>
        </div>
        <div className="bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg p-4">
          <p className="text-sm text-[var(--text-secondary)]">Pending</p>
          <p className="text-2xl font-semibold mt-1 text-yellow-400">{stats.total - stats.applied}</p>
        </div>
      </div>

      <div className="flex gap-2">
        {(['all', 'simple', 'moderate', 'complex'] as const).map((complexity) => {
          const label = complexity.charAt(0).toUpperCase() + complexity.slice(1);
          const count = complexity === 'all' ? stats.total : stats[complexity as keyof typeof stats];
          return (
            <button
              key={complexity}
              onClick={() => setFilterComplexity(complexity)}
              className={`px-4 py-2 rounded font-medium text-sm transition-colors ${
                filterComplexity === complexity
                  ? 'bg-purple-600 text-white'
                  : 'bg-[var(--bg-secondary)] border border-[var(--border-color)] hover:border-purple-500'
              }`}
            >
              {label} ({count})
            </button>
          );
        })}
      </div>

      {error && (
        <div className="bg-red-900 border border-red-700 rounded p-4">
          <p className="text-red-200 text-sm">{error}</p>
        </div>
      )}

      <div className="space-y-3">
        {loading ? (
          <p className="text-[var(--text-secondary)]">Loading patches...</p>
        ) : filtered.length === 0 ? (
          <p className="text-[var(--text-secondary)]">No patches found</p>
        ) : (
          filtered.map((patch) => (
            <div
              key={patch.id}
              className="bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg p-4"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-medium">Patch {patch.id.substring(0, 8)}</h3>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${complexityColors[patch.apply_complexity as keyof typeof complexityColors]}`}>
                      {patch.apply_complexity}
                    </span>
                    {patch.applied && (
                      <span className="px-2 py-1 rounded text-xs font-medium bg-green-900 text-green-200">
                        Applied
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-[var(--text-secondary)] mb-2">
                    Confidence: {(patch.confidence * 100).toFixed(0)}%
                  </p>
                  <p className="text-sm mb-3">{patch.explanation}</p>

                  <div className="bg-[var(--bg-primary)] rounded-lg p-3 mb-3 text-xs font-mono overflow-x-auto">
                    <p className="text-[var(--text-secondary)] mb-1">Original:</p>
                    <pre className="text-red-300 mb-3">{patch.original_code}</pre>
                    <p className="text-[var(--text-secondary)] mb-1">Patched:</p>
                    <pre className="text-green-300">{patch.patched_code}</pre>
                  </div>
                </div>
                {!patch.applied && patch.can_auto_apply && (
                  <button
                    onClick={() => handleApplyPatch(patch.id)}
                    disabled={applyingId === patch.id}
                    className="ml-4 px-3 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded text-xs font-medium whitespace-nowrap"
                  >
                    {applyingId === patch.id ? 'Applying...' : 'Apply'}
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default function PatchesPage() {
  return (
    <ProtectedRoute requiredPermission="read_scan">
      <PatchesContent />
    </ProtectedRoute>
  );
}

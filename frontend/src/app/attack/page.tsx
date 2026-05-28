'use client';

import { useEffect, useState } from 'react';
import { useAttacks } from '@/hooks/useAttacks';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Attack } from '@/types';

function AttackContent() {
  const { attacks, listAttacks, getHighImpactAttacks, loading, error } = useAttacks();
  const [filterType, setFilterType] = useState<'all' | 'high-impact' | 'high-probability'>('all');

  useEffect(() => {
    if (filterType === 'all') {
      listAttacks(0, 100);
    } else if (filterType === 'high-impact') {
      getHighImpactAttacks();
    } else {
      getHighImpactAttacks();
    }
  }, [filterType]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Attack Scenarios</h1>
        <p className="text-[var(--text-secondary)] mt-1">
          Simulated attack paths and exploitation scenarios
        </p>
      </div>

      <div className="flex gap-2">
        {(['all', 'high-impact', 'high-probability'] as const).map((type) => {
          const labels = {
            all: 'All Attacks',
            'high-impact': 'High Impact',
            'high-probability': 'High Probability',
          };
          return (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-4 py-2 rounded font-medium text-sm transition-colors ${
                filterType === type
                  ? 'bg-red-600 text-white'
                  : 'bg-[var(--bg-secondary)] border border-[var(--border-color)] hover:border-red-500'
              }`}
            >
              {labels[type]} ({attacks.length})
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
          <p className="text-[var(--text-secondary)]">Loading attack scenarios...</p>
        ) : attacks.length === 0 ? (
          <p className="text-[var(--text-secondary)]">No attack scenarios found</p>
        ) : (
          attacks
            .sort((a, b) => b.impact_score - a.impact_score)
            .map((attack) => (
              <div
                key={attack.id}
                className="bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg p-4"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-medium text-lg">{attack.attack_type}</h3>
                    <p className="text-sm text-[var(--text-secondary)]">{attack.attack_vector} Vector</p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm">
                      <p className="font-medium">Impact Score</p>
                      <p className="text-lg text-red-400">{attack.impact_score.toFixed(1)}/10</p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-3 text-sm">
                  <div>
                    <p className="text-[var(--text-secondary)]">Success Probability</p>
                    <div className="w-full bg-[var(--border-color)] rounded-full h-2 mt-1">
                      <div
                        className="bg-red-500 h-2 rounded-full"
                        style={{ width: `${attack.success_probability * 100}%` }}
                      />
                    </div>
                    <p className="text-xs mt-1">{(attack.success_probability * 100).toFixed(0)}%</p>
                  </div>
                  <div>
                    <p className="text-[var(--text-secondary)]">MITRE Tactic</p>
                    <p className="font-mono text-xs mt-1">{attack.mitre_tactic || 'N/A'}</p>
                  </div>
                </div>

                {attack.attack_path && attack.attack_path.length > 0 && (
                  <div className="mb-3">
                    <p className="text-sm font-medium mb-2">Attack Path:</p>
                    <ol className="list-decimal list-inside space-y-1 text-sm text-[var(--text-secondary)]">
                      {attack.attack_path.map((step, idx) => (
                        <li key={idx}>{step}</li>
                      ))}
                    </ol>
                  </div>
                )}

                {attack.prerequisites && attack.prerequisites.length > 0 && (
                  <div className="mb-3">
                    <p className="text-sm font-medium mb-2">Prerequisites:</p>
                    <ul className="list-disc list-inside space-y-1 text-sm text-[var(--text-secondary)]">
                      {attack.prerequisites.map((prereq, idx) => (
                        <li key={idx}>{prereq}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {attack.mitigation && (
                  <p className="text-sm text-green-300">
                    <span className="font-medium">Mitigation:</span> {attack.mitigation}
                  </p>
                )}
              </div>
            ))
        )}
      </div>
    </div>
  );
}

export default function AttackPage() {
  return (
    <ProtectedRoute requiredPermission="read_scan">
      <AttackContent />
    </ProtectedRoute>
  );
}

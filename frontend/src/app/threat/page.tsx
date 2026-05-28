'use client';

import { useEffect, useState } from 'react';
import { useFindings } from '@/hooks/useFindings';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Finding, SeverityLevel } from '@/types';

function ThreatContent() {
  const { findings, listFindings, loading, error, ignoreFinding } = useFindings();
  const [filterSeverity, setFilterSeverity] = useState<SeverityLevel | 'all'>('all');
  const [ignoreReason, setIgnoreReason] = useState('');

  useEffect(() => {
    listFindings(0, 100);
  }, []);

  const filtered = filterSeverity === 'all'
    ? findings
    : findings.filter(f => f.severity === filterSeverity);

  const severityColors = {
    critical: 'bg-red-900 text-red-200',
    high: 'bg-orange-900 text-orange-200',
    medium: 'bg-yellow-900 text-yellow-200',
    low: 'bg-blue-900 text-blue-200',
    info: 'bg-gray-900 text-gray-200',
  };

  const severityOrder = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Vulnerability Findings</h1>
        <p className="text-[var(--text-secondary)] mt-1">
          All security vulnerabilities discovered during scans
        </p>
      </div>

      <div className="flex gap-2">
        {(['all', 'critical', 'high', 'medium', 'low'] as const).map((severity) => {
          const count = severity === 'all'
            ? findings.length
            : findings.filter(f => f.severity === severity).length;
          return (
            <button
              key={severity}
              onClick={() => setFilterSeverity(severity)}
              className={`px-4 py-2 rounded font-medium text-sm transition-colors ${
                filterSeverity === severity
                  ? 'bg-blue-600 text-white'
                  : 'bg-[var(--bg-secondary)] border border-[var(--border-color)] hover:border-blue-500'
              }`}
            >
              {severity.charAt(0).toUpperCase() + severity.slice(1)} ({count})
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
          <p className="text-[var(--text-secondary)]">Loading vulnerabilities...</p>
        ) : filtered.length === 0 ? (
          <p className="text-[var(--text-secondary)]">No vulnerabilities found</p>
        ) : (
          filtered.sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity]).map((finding) => (
            <div
              key={finding.id}
              className="bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg p-4"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-medium">{finding.vulnerability_type}</h3>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${severityColors[finding.severity]}`}>
                      {finding.severity}
                    </span>
                  </div>
                  <p className="text-sm text-[var(--text-secondary)] mb-2">{finding.description}</p>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <p><span className="font-medium">File:</span> {finding.file_path}:{finding.line_number}</p>
                    <p><span className="font-medium">CWE:</span> {finding.cwe_id || 'N/A'}</p>
                    <p><span className="font-medium">Confidence:</span> {(finding.confidence * 100).toFixed(0)}%</p>
                    <p><span className="font-medium">Exploitability:</span> {(finding.exploitability_score * 10).toFixed(1)}/10</p>
                  </div>
                  {finding.code_snippet && (
                    <div className="mt-3 bg-[var(--bg-primary)] rounded p-2 font-mono text-xs overflow-x-auto">
                      <code>{finding.code_snippet}</code>
                    </div>
                  )}
                  {finding.recommendation && (
                    <p className="mt-3 text-sm text-green-300">
                      <span className="font-medium">Fix:</span> {finding.recommendation}
                    </p>
                  )}
                </div>
                {!finding.is_ignored && (
                  <button
                    onClick={() => ignoreFinding(finding.id, 'false positive')}
                    className="ml-4 px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs font-medium whitespace-nowrap"
                  >
                    Ignore
                  </button>
                )}
              </div>
              {finding.is_ignored && (
                <p className="mt-2 text-xs text-gray-400">Marked as ignored: {finding.ignore_reason}</p>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default function ThreatPage() {
  return (
    <ProtectedRoute requiredPermission="read_scan">
      <ThreatContent />
    </ProtectedRoute>
  );
}

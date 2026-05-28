'use client';

import { useEffect, useState } from 'react';
import { useScans } from '@/hooks/useScans';
import { useReports } from '@/hooks/useReports';
import RiskStatsCard from '@/components/cards/RiskStatsCard';
import AgentStatusCard from '@/components/status/AgentStatusCard';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Scan } from '@/types';

function DashboardContent() {
  const { scans, listScans, loading } = useScans();
  const { metrics, getReportMetrics } = useReports();
  const [selectedScan, setSelectedScan] = useState<Scan | null>(null);

  useEffect(() => {
    listScans(0, 10);
  }, []);

  useEffect(() => {
    if (scans.length > 0 && !selectedScan) {
      setSelectedScan(scans[0]);
      getReportMetrics(scans[0].id);
    }
  }, [scans]);

  const completedScans = scans.filter(s => s.status === 'completed').length;
  const failedScans = scans.filter(s => s.status === 'failed').length;

  const stats = metrics ? [
    { label: 'Overall Risk', value: `${metrics.average_cvss_score?.toFixed(1) || 'N/A'}/10`, trend: 'Security Grade' },
    { label: 'Active Findings', value: metrics.total_vulnerabilities || '0', trend: `${metrics.vulnerabilities_by_severity.critical} critical` },
    { label: 'Completed Scans', value: completedScans.toString(), trend: `${failedScans} failed` },
  ] : [
    { label: 'Overall Risk', value: '-', trend: 'Loading...' },
    { label: 'Active Findings', value: '-', trend: 'Loading...' },
    { label: 'Completed Scans', value: completedScans.toString(), trend: `${failedScans} failed` },
  ];

  const agents = [
    { name: 'Scanner Agent', status: 'idle', detail: 'Code analysis ready' },
    { name: 'Threat Agent', status: 'idle', detail: 'Threat classification ready' },
    { name: 'Attack Agent', status: 'idle', detail: 'Attack simulation ready' },
    { name: 'Patch Agent', status: 'idle', detail: 'Patch generation ready' },
    { name: 'Report Agent', status: 'idle', detail: 'Report generation ready' },
  ];

  const recentScans = scans.slice(0, 5).map(scan => ({
    id: scan.id,
    status: scan.status,
    progress: scan.progress,
    created_at: new Date(scan.created_at).toLocaleDateString(),
  }));

  return (
    <div className="space-y-6">
      <div>
        <p className="hud-label">SentinelOS</p>
        <h1 className="text-2xl font-semibold mt-2">
          Tactical Security Command Center
        </h1>
        <p className="text-sm text-[var(--text-secondary)] mt-2">
          Unified automated security scanning and vulnerability management.
        </p>
      </div>

      <RiskStatsCard
        title="Security Posture Snapshot"
        stats={stats}
      />

      <div className="grid gap-4 lg:grid-cols-12">
        <div className="lg:col-span-7 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-4">Recent Scans</h2>
          {loading ? (
            <p className="text-[var(--text-secondary)]">Loading scans...</p>
          ) : scans.length === 0 ? (
            <p className="text-[var(--text-secondary)]">No scans yet. Start a new scan to begin.</p>
          ) : (
            <div className="space-y-2">
              {recentScans.map(scan => (
                <div
                  key={scan.id}
                  className="flex items-center justify-between p-3 bg-[var(--bg-primary)] rounded border border-[var(--border-color)]"
                >
                  <div className="flex-1">
                    <p className="text-sm font-medium">{scan.id.substring(0, 8)}</p>
                    <p className="text-xs text-[var(--text-secondary)]">{scan.created_at}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-24 bg-[var(--border-color)] rounded-full h-2">
                      <div
                        className="bg-green-500 h-2 rounded-full transition-all"
                        style={{ width: `${scan.progress}%` }}
                      />
                    </div>
                    <span className={`text-xs px-2 py-1 rounded ${
                      scan.status === 'completed' ? 'bg-green-900 text-green-200' :
                      scan.status === 'failed' ? 'bg-red-900 text-red-200' :
                      scan.status === 'running' ? 'bg-blue-900 text-blue-200' :
                      'bg-gray-900 text-gray-200'
                    }`}>
                      {scan.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="lg:col-span-5">
          <AgentStatusCard
            title="Security Agents"
            agents={agents.map(a => ({ ...a, status: 'success' }))}
          />
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute requiredPermission="read_scan">
      <DashboardContent />
    </ProtectedRoute>
  );
}

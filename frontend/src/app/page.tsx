import AgentStatusCard from "@/components/status/AgentStatusCard";
import RiskStatsCard from "@/components/cards/RiskStatsCard";
import TerminalLogs from "@/components/logs/TerminalLogs";

const agentData = [
  { name: "Scanner Agent", status: "success", detail: "Idle - last scan 2m" },
  { name: "Analysis Agent", status: "running", detail: "Correlating CVEs" },
  { name: "Patching Agent", status: "idle", detail: "Awaiting tasks" },
];

const logs = [
  { level: "SYS", timestamp: "07:24:12", message: "SentinelOS boot sequence completed." },
  { level: "INFO", timestamp: "07:24:20", message: "Threat feeds synchronized (12 sources)." },
  { level: "WARN", timestamp: "07:24:44", message: "Anomalous privilege spike detected in dev branch." },
  { level: "EXEC", timestamp: "07:25:02", message: "Deployed monitoring hooks across 48 services." },
  { level: "INFO", timestamp: "07:25:16", message: "SOC dashboard refreshed." },
];

export default function OverviewPage() {
  return (
    <div className="space-y-6">
      <div>
        <p className="hud-label">SentinelOS</p>
        <h1 className="text-2xl font-semibold mt-2">
          Tactical Security Command Center
        </h1>
        <p className="text-sm text-[var(--text-secondary)] mt-2">
          Unified offensive and defensive AI workflows for enterprise-scale environments.
        </p>
      </div>

      <RiskStatsCard
        title="Operational Risk Snapshot"
        stats={[
          { label: "Overall Risk", value: "42%", trend: "-8% vs last 24h" },
          { label: "Active Findings", value: "74", trend: "12 critical" },
          { label: "Assets Covered", value: "312", trend: "Full coverage" },
        ]}
      />

      <div className="grid gap-4 lg:grid-cols-12">
        <div className="lg:col-span-7">
          <TerminalLogs title="Live Command Feed" logs={logs} />
        </div>
        <div className="lg:col-span-5">
          <AgentStatusCard title="System Agents" agents={agentData} />
        </div>
      </div>
    </div>
  );
}

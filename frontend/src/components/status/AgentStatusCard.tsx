import StatusDot from "@/components/status/StatusDot";

export interface AgentStatus {
  name: string;
  status: "idle" | "running" | "failed" | "success";
  detail: string;
}

interface AgentStatusCardProps {
  title: string;
  agents: AgentStatus[];
}

export default function AgentStatusCard({ title, agents }: AgentStatusCardProps) {
  return (
    <section className="hud-panel">
      <div className="hud-panel-header">
        <div>
          <p className="hud-label">Agent Status</p>
          <p className="text-sm font-semibold mt-1">{title}</p>
        </div>
        <span className="hud-label">Live</span>
      </div>
      <div className="grid gap-3 p-4">
        {agents.map((agent) => (
          <div
            key={agent.name}
            className="flex items-center justify-between border border-[var(--border)] rounded-[var(--radius)] px-3 py-2"
          >
            <div>
              <p className="text-xs uppercase tracking-[0.2em] font-mono">
                {agent.name}
              </p>
              <p className="text-[11px] text-[var(--text-secondary)]">
                {agent.detail}
              </p>
            </div>
            <StatusDot status={agent.status} />
          </div>
        ))}
      </div>
    </section>
  );
}

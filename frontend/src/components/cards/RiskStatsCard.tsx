interface RiskStat {
  label: string;
  value: string;
  trend?: string;
}

interface RiskStatsCardProps {
  title: string;
  stats: RiskStat[];
}

export default function RiskStatsCard({ title, stats }: RiskStatsCardProps) {
  return (
    <section className="hud-panel">
      <div className="hud-panel-header">
        <div>
          <p className="hud-label">Risk Metrics</p>
          <p className="text-sm font-semibold mt-1">{title}</p>
        </div>
      </div>
      <div className="grid gap-4 p-4 md:grid-cols-3">
        {stats.map((stat) => (
          <div key={stat.label} className="border border-[var(--border)] rounded-[var(--radius)] p-3">
            <p className="hud-label">{stat.label}</p>
            <p className="hud-kpi mt-2">{stat.value}</p>
            {stat.trend ? (
              <p className="text-[11px] text-[var(--text-secondary)] mt-1">
                {stat.trend}
              </p>
            ) : null}
          </div>
        ))}
      </div>
    </section>
  );
}

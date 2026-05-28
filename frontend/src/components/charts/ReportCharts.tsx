"use client";

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  AreaChart,
  Area,
} from "recharts";

const severityData = [
  { name: "Critical", value: 12, color: "#F85149" },
  { name: "High", value: 18, color: "#F5A623" },
  { name: "Medium", value: 22, color: "#4EA1FF" },
  { name: "Low", value: 30, color: "#8B949E" },
];

const timelineData = [
  { name: "Day 1", value: 48 },
  { name: "Day 2", value: 42 },
  { name: "Day 3", value: 34 },
  { name: "Day 4", value: 27 },
  { name: "Day 5", value: 19 },
];

const trendData = [
  { name: "Week 1", value: 62 },
  { name: "Week 2", value: 54 },
  { name: "Week 3", value: 41 },
  { name: "Week 4", value: 29 },
];

export default function ReportCharts() {
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <div className="hud-panel p-4">
        <p className="hud-label">Severity Distribution</p>
        <div className="h-52 mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={severityData} dataKey="value" innerRadius={45} outerRadius={70}>
                {severityData.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="grid grid-cols-2 gap-2 text-[11px] text-[var(--text-secondary)] mt-2">
          {severityData.map((entry) => (
            <div key={entry.name} className="flex items-center gap-2">
              <span
                className="h-2 w-2"
                style={{ backgroundColor: entry.color }}
              />
              <span>{entry.name}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="hud-panel p-4">
        <p className="hud-label">Risk Timeline</p>
        <div className="h-52 mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={timelineData}>
              <XAxis dataKey="name" stroke="#30363D" tick={{ fill: "#8B949E", fontSize: 10 }} />
              <YAxis stroke="#30363D" tick={{ fill: "#8B949E", fontSize: 10 }} />
              <Tooltip
                contentStyle={{
                  background: "#161B22",
                  border: "1px solid #30363D",
                  color: "#FFFFFF",
                }}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#00D4AA"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="hud-panel p-4">
        <p className="hud-label">Vulnerability Trend</p>
        <div className="h-52 mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trendData}>
              <XAxis dataKey="name" stroke="#30363D" tick={{ fill: "#8B949E", fontSize: 10 }} />
              <YAxis stroke="#30363D" tick={{ fill: "#8B949E", fontSize: 10 }} />
              <Tooltip
                contentStyle={{
                  background: "#161B22",
                  border: "1px solid #30363D",
                  color: "#FFFFFF",
                }}
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke="#4EA1FF"
                fill="rgba(78,161,255,0.2)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

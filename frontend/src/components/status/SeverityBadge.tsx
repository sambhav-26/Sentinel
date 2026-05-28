import { cn } from "@/lib/utils";

interface SeverityBadgeProps {
  severity: "Critical" | "High" | "Medium" | "Low";
}

const severityStyles: Record<SeverityBadgeProps["severity"], string> = {
  Critical: "border-[var(--critical)] text-[var(--critical)]",
  High: "border-[var(--warning)] text-[var(--warning)]",
  Medium: "border-[#4ea1ff] text-[#4ea1ff]",
  Low: "border-[var(--text-secondary)] text-[var(--text-secondary)]",
};

export default function SeverityBadge({ severity }: SeverityBadgeProps) {
  return (
    <span
      className={cn(
        "border rounded-[var(--radius)] px-2 py-1 text-[10px] uppercase tracking-[0.2em] font-mono",
        severityStyles[severity]
      )}
    >
      {severity}
    </span>
  );
}

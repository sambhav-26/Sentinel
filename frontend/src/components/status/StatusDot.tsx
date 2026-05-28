import { cn } from "@/lib/utils";

interface StatusDotProps {
  status: "idle" | "running" | "failed" | "success";
  className?: string;
}

const statusColor: Record<StatusDotProps["status"], string> = {
  idle: "bg-[var(--text-secondary)]",
  running: "bg-[var(--warning)]",
  failed: "bg-[var(--critical)]",
  success: "bg-[var(--primary)]",
};

export default function StatusDot({ status, className }: StatusDotProps) {
  return (
    <span
      className={cn(
        "h-2.5 w-2.5 rounded-[var(--radius)] inline-block",
        statusColor[status],
        className
      )}
    />
  );
}

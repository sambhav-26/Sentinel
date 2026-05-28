import { cn } from "@/lib/utils";

export interface WorkflowStep {
  label: string;
  status: "complete" | "active" | "pending";
}

interface WorkflowStepperProps {
  steps: WorkflowStep[];
}

export default function WorkflowStepper({ steps }: WorkflowStepperProps) {
  return (
    <div className="hud-panel p-4">
      <div className="grid gap-3 md:grid-cols-4">
        {steps.map((step, index) => (
          <div key={step.label} className="flex items-center gap-3">
            <div
              className={cn(
                "h-9 w-9 border border-[var(--border)] rounded-[var(--radius)] flex items-center justify-center text-xs font-mono",
                step.status === "active" &&
                  "border-[var(--primary)] text-[var(--primary)]",
                step.status === "complete" &&
                  "border-[var(--primary)] text-[var(--primary)]",
                step.status === "pending" && "text-[var(--text-secondary)]"
              )}
            >
              {index + 1}
            </div>
            <div>
              <p className="hud-label">Step</p>
              <p className="text-sm font-semibold">{step.label}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

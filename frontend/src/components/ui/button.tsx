import * as React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "primary" | "ghost";
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "hud-button",
          variant === "primary" && "hud-button-primary",
          variant === "ghost" &&
            "border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]",
          className
        )}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button };

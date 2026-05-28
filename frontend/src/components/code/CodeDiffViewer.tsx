interface CodeDiffBlock {
  title: string;
  lines: { code: string; highlight?: "add" | "remove" }[];
}

interface CodeDiffViewerProps {
  left: CodeDiffBlock;
  right: CodeDiffBlock;
}

export default function CodeDiffViewer({ left, right }: CodeDiffViewerProps) {
  return (
    <section className="hud-panel">
      <div className="hud-panel-header">
        <div>
          <p className="hud-label">Code Diff</p>
          <p className="text-sm font-semibold mt-1">Remediation Patch</p>
        </div>
      </div>
      <div className="grid md:grid-cols-2">
        {[left, right].map((block, blockIndex) => (
          <div
            key={block.title}
            className={`border-t border-[var(--border)] p-4 ${
              blockIndex === 0 ? "border-r" : ""
            } border-[var(--border)]`}
          >
            <p className="hud-label mb-3">{block.title}</p>
            <div className="space-y-1 font-mono text-xs">
              {block.lines.map((line, index) => (
                <div
                  key={`${block.title}-${index}`}
                  className={`px-2 py-1 rounded-[var(--radius)] ${
                    line.highlight === "add"
                      ? "bg-[rgba(0,212,170,0.12)] text-[var(--primary)]"
                      : line.highlight === "remove"
                      ? "bg-[rgba(248,81,73,0.12)] text-[var(--critical)]"
                      : "text-[var(--text-primary)]"
                  }`}
                >
                  {line.code}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

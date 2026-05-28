"use client";

import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  type Node,
  type Edge,
  type NodeProps,
} from "reactflow";
import "reactflow/dist/style.css";
import StatusDot from "@/components/status/StatusDot";

interface AttackChainGraphProps {
  activeNodeId: string;
}

const baseNodes: Node[] = [
  {
    id: "initial",
    position: { x: 0, y: 0 },
    data: { label: "Initial Access", status: "success" },
    type: "statusNode",
  },
  {
    id: "inject",
    position: { x: 0, y: 110 },
    data: { label: "Code Injection", status: "success" },
    type: "statusNode",
  },
  {
    id: "privilege",
    position: { x: 0, y: 220 },
    data: { label: "Privilege Escalation", status: "running" },
    type: "statusNode",
  },
  {
    id: "exfil",
    position: { x: 0, y: 330 },
    data: { label: "Data Exfiltration", status: "idle" },
    type: "statusNode",
  },
];

const edges: Edge[] = [
  { id: "e1", source: "initial", target: "inject" },
  { id: "e2", source: "inject", target: "privilege" },
  { id: "e3", source: "privilege", target: "exfil" },
];

export default function AttackChainGraph({ activeNodeId }: AttackChainGraphProps) {
  const StatusNode = ({ data, id }: NodeProps<{ label: string; status: "idle" | "running" | "failed" | "success" }>) => {
    const isActive = id === activeNodeId;
    return (
      <div
        style={{
          border: `1px solid ${isActive ? "#00D4AA" : "#30363D"}`,
          borderRadius: 4,
          padding: "10px 12px",
          width: 180,
          backgroundColor: "#161B22",
          color: isActive ? "#00D4AA" : "#FFFFFF",
          fontFamily: "var(--font-jetbrains-mono)",
          textTransform: "uppercase",
          letterSpacing: "0.2em",
          fontSize: "11px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 8,
        }}
      >
        <span>{data.label}</span>
        <StatusDot status={data.status} />
      </div>
    );
  };

  const nodes = baseNodes.map((node) => ({
    ...node,
    data: {
      ...node.data,
      status: node.id === activeNodeId ? "running" : node.data.status,
    },
  }));

  return (
    <section className="hud-panel h-full">
      <div className="hud-panel-header">
        <div>
          <p className="hud-label">Attack Chain</p>
          <p className="text-sm font-semibold mt-1">Simulation Flow</p>
        </div>
      </div>
      <div className="h-[420px] border-t border-[var(--border)]">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={{ statusNode: StatusNode }}
          fitView
          panOnDrag={false}
          zoomOnScroll={false}
          zoomOnPinch={false}
          nodesConnectable={false}
          nodesDraggable={false}
        >
          <Background color="#30363D" gap={16} />
          <MiniMap
            nodeColor="#00D4AA"
            maskColor="rgba(13,17,23,0.6)"
            style={{ backgroundColor: "#0D1117" }}
          />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>
    </section>
  );
}

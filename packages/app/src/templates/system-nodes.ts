import {
  generateReferenceNum,
  resetReferenceNums,
  type DiagramNode,
  type DiagramEdge,
  type DiagramData,
  NODE_DEFAULTS,
} from "./flowchart-nodes"

export type SystemNodeType = "server" | "database" | "client" | "api" | "storage" | "cloud" | "service" | "queue"

export interface SystemNode extends DiagramNode {
  systemType: SystemNodeType
}

export const SYSTEM_NODE_DEFAULTS: Record<SystemNodeType, { width: number; height: number; icon: string }> = {
  server: { width: 80, height: 80, icon: "server" },
  database: { width: 70, height: 90, icon: "database" },
  client: { width: 80, height: 60, icon: "client" },
  api: { width: 80, height: 60, icon: "api" },
  storage: { width: 80, height: 70, icon: "storage" },
  cloud: { width: 100, height: 60, icon: "cloud" },
  service: { width: 80, height: 60, icon: "service" },
  queue: { width: 90, height: 50, icon: "queue" },
}

export function createSystemNode(
  systemType: SystemNodeType,
  label: string,
  x: number,
  y: number,
  id?: string,
): SystemNode {
  const defaults = SYSTEM_NODE_DEFAULTS[systemType]
  return {
    id: id ?? `${systemType}-${Date.now()}`,
    type: "process",
    systemType,
    label,
    x,
    y,
    width: defaults.width,
    height: defaults.height,
    referenceNum: generateReferenceNum(),
  }
}

export function createSystemTemplate(title: string = "System Architecture"): DiagramData {
  resetReferenceNums()

  const nodes: DiagramNode[] = [
    createSystemNode("client", "User", 100, 50),
    createSystemNode("cloud", "Cloud", 100, 150),
    createSystemNode("api", "API Gateway", 50, 270),
    createSystemNode("service", "Service A", 180, 270),
    createSystemNode("service", "Service B", 180, 370),
    createSystemNode("queue", "Message Queue", 50, 370),
    createSystemNode("database", "Database", 50, 470),
    createSystemNode("storage", "Storage", 180, 470),
  ]

  const edges: DiagramEdge[] = [
    { id: "e1", from: nodes[0].id, to: nodes[1].id, type: "arrow" },
    { id: "e2", from: nodes[1].id, to: nodes[2].id, type: "arrow" },
    { id: "e3", from: nodes[1].id, to: nodes[3].id, type: "arrow" },
    { id: "e4", from: nodes[2].id, to: nodes[5].id, type: "arrow" },
    { id: "e5", from: nodes[3].id, to: nodes[4].id, type: "arrow" },
    { id: "e6", from: nodes[2].id, to: nodes[6].id, type: "arrow" },
    { id: "e7", from: nodes[3].id, to: nodes[7].id, type: "arrow" },
  ]

  return { nodes, edges, title }
}

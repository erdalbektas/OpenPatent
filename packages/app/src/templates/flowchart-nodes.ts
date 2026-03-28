import { USPTO, getUsableArea } from "./uspto-config"

export type NodeType = "process" | "decision" | "start" | "end" | "input" | "output" | "subprocess"

export interface DiagramNode {
  id: string
  type: NodeType
  label: string
  x: number
  y: number
  width: number
  height: number
  referenceNum?: number
}

export interface DiagramEdge {
  id: string
  from: string
  to: string
  label?: string
  type: "arrow" | "line" | "dashed"
}

export interface DiagramData {
  nodes: DiagramNode[]
  edges: DiagramEdge[]
  title?: string
  figureNumber?: string
}

export const NODE_DEFAULTS: Record<NodeType, { width: number; height: number }> = {
  process: { width: 120, height: 60 },
  decision: { width: 80, height: 80 },
  start: { width: 100, height: 40 },
  end: { width: 100, height: 40 },
  input: { width: 120, height: 60 },
  output: { width: 120, height: 60 },
  subprocess: { width: 120, height: 60 },
}

let refCounter = USPTO.reference.start

export function generateReferenceNum(): number {
  const num = refCounter
  refCounter += USPTO.reference.increment
  return num
}

export function resetReferenceNums(start = USPTO.reference.start) {
  refCounter = start
}

export function createNode(type: NodeType, label: string, x: number, y: number, id?: string): DiagramNode {
  const defaults = NODE_DEFAULTS[type]
  return {
    id: id ?? `${type}-${Date.now()}`,
    type,
    label,
    x,
    y,
    width: defaults.width,
    height: defaults.height,
    referenceNum: generateReferenceNum(),
  }
}

export function createEdge(from: string, to: string, label?: string): DiagramEdge {
  return {
    id: `edge-${from}-${to}`,
    from,
    to,
    label,
    type: "arrow",
  }
}

export function autoLayout(nodes: DiagramNode[], edges: DiagramEdge[]): DiagramNode[] {
  const area = getUsableArea()
  const nodeMap = new Map(nodes.map((n) => [n.id, n]))
  const inDegree = new Map<string, number>()
  const outDegree = new Map<string, number>()

  for (const edge of edges) {
    inDegree.set(edge.to, (inDegree.get(edge.to) ?? 0) + 1)
    outDegree.set(edge.from, (outDegree.get(edge.from) ?? 0) + 1)
  }

  const levels = new Map<string, number>()
  const visited = new Set<string>()
  const queue: string[] = []

  for (const node of nodes) {
    if ((inDegree.get(node.id) ?? 0) === 0) {
      queue.push(node.id)
      levels.set(node.id, 0)
    }
  }

  while (queue.length) {
    const current = queue.shift()!
    if (visited.has(current)) continue
    visited.add(current)

    const currentLevel = levels.get(current) ?? 0

    for (const edge of edges) {
      if (edge.from === current) {
        const nextLevel = levels.get(edge.to) ?? -1
        if (currentLevel + 1 > nextLevel) {
          levels.set(edge.to, currentLevel + 1)
        }
        if (!visited.has(edge.to)) {
          queue.push(edge.to)
        }
      }
    }
  }

  const levelNodes = new Map<number, DiagramNode[]>()
  for (const node of nodes) {
    const level = levels.get(node.id) ?? 0
    if (!levelNodes.has(level)) levelNodes.set(level, [])
    levelNodes.get(level)!.push(node)
  }

  const spacing = { x: 50, y: 80 }
  const startX = area.x + 50
  const startY = area.y + 50

  const positioned = nodes.map((node) => {
    const level = levels.get(node.id) ?? 0
    const levelArr = levelNodes.get(level) ?? []
    const indexInLevel = levelArr.indexOf(node)

    return {
      ...node,
      x: startX + level * (NODE_DEFAULTS[node.type].width + spacing.x),
      y: startY + indexInLevel * (NODE_DEFAULTS[node.type].height + spacing.y),
    }
  })

  return positioned
}

export function createFlowchartTemplate(description: string): DiagramData {
  const nodes: DiagramNode[] = []
  const edges: DiagramEdge[] = []

  resetReferenceNums()

  nodes.push(createNode("start", "Start", 100, 50))
  nodes.push(createNode("process", description || "Process", 100, 120))
  nodes.push(createNode("decision", "Check?", 100, 210))
  nodes.push(createNode("process", "Action", 100, 320))
  nodes.push(createNode("end", "End", 100, 410))

  edges.push(createEdge(nodes[0].id, nodes[1].id))
  edges.push(createEdge(nodes[1].id, nodes[2].id))
  edges.push(createEdge(nodes[2].id, nodes[3].id, "Yes"))
  edges.push(createEdge(nodes[2].id, nodes[4].id, "No"))
  edges.push(createEdge(nodes[3].id, nodes[4].id))

  return { nodes, edges }
}

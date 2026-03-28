import { USPTO, getUsableArea, FIGURE_NUMBER_OFFSET } from "../templates/uspto-config"
import type { DiagramNode, DiagramEdge, DiagramData, NodeType } from "../templates/flowchart-nodes"
import type { SystemNode, SystemNodeType } from "../templates/system-nodes"

export interface RenderOptions {
  patentMode?: boolean
  figureNumber?: string
  showGrid?: boolean
  scale?: number
}

export function renderNode(node: DiagramNode, options: RenderOptions = {}): string {
  const { patentMode = false } = options
  const strokeColor = USPTO.colors.black
  const fillColor = USPTO.colors.white
  const strokeWidth = USPTO.lineWeights.visible

  const refX = node.x + node.width + 4
  const refY = node.y - 4

  let shape = ""

  switch (node.type) {
    case "process":
      shape = `<rect x="${node.x}" y="${node.y}" width="${node.width}" height="${node.height}" fill="${fillColor}" stroke="${strokeColor}" stroke-width="${strokeWidth}"/>`
      break
    case "decision":
      const cx = node.x + node.width / 2
      const cy = node.y + node.height / 2
      const hw = node.width / 2
      const hh = node.height / 2
      shape = `<polygon points="${cx},${node.y} ${node.x + node.width},${cy} ${cx},${node.y + node.height} ${node.x},${cy}" fill="${fillColor}" stroke="${strokeColor}" stroke-width="${strokeWidth}"/>`
      break
    case "start":
    case "end":
      const r = Math.min(node.width / 2, node.height / 2)
      const rx = node.width / 2
      const ry = node.height / 2
      shape = `<ellipse cx="${node.x + rx}" cy="${node.y + ry}" rx="${rx}" ry="${ry}" fill="${fillColor}" stroke="${strokeColor}" stroke-width="${strokeWidth}"/>`
      break
    case "input":
    case "output":
      const parallelX = node.x + 10
      shape = `<polygon points="${parallelX},${node.y} ${node.x + node.width},${node.y} ${node.x + node.width - 10},${node.y + node.height} ${node.x + 10},${node.y + node.height}" fill="${fillColor}" stroke="${strokeColor}" stroke-width="${strokeWidth}"/>`
      break
    case "subprocess":
      shape = `<rect x="${node.x}" y="${node.y}" width="${node.width}" height="${node.height}" fill="${fillColor}" stroke="${strokeColor}" stroke-width="${strokeWidth}"/>`
      shape += `<line x1="${node.x}" y1="${node.y}" x2="${node.x + 15}" y2="${node.y}" stroke="${strokeColor}" stroke-width="${strokeWidth}"/>`
      shape += `<line x1="${node.x}" y1="${node.y + node.height}" x2="${node.x + 15}" y2="${node.y + node.height}" stroke="${strokeColor}" stroke-width="${strokeWidth}"/>`
      break
    default:
      shape = `<rect x="${node.x}" y="${node.y}" width="${node.width}" height="${node.height}" fill="${fillColor}" stroke="${strokeColor}" stroke-width="${strokeWidth}"/>`
  }

  const labelX = node.x + node.width / 2
  const labelY = node.y + node.height / 2 + 4

  const label = `<text x="${labelX}" y="${labelY}" text-anchor="middle" font-family="${USPTO.fonts.label}" font-size="${USPTO.fontSizes.label}" fill="${strokeColor}">${escapeXml(node.label)}</text>`

  const refNum =
    patentMode && node.referenceNum
      ? `<text x="${refX}" y="${refY}" font-family="${USPTO.fonts.reference}" font-size="${USPTO.fontSizes.reference}" fill="${strokeColor}">${node.referenceNum}</text>`
      : ""

  return shape + label + refNum
}

export function renderSystemNode(node: SystemNode, options: RenderOptions = {}): string {
  const { patentMode = false } = options
  const strokeColor = USPTO.colors.black
  const fillColor = USPTO.colors.white
  const strokeWidth = USPTO.lineWeights.visible

  const refX = node.x + node.width + 4
  const refY = node.y - 4

  let shape = ""

  switch (node.systemType) {
    case "database":
      const dbHeight = node.height
      const dbY = node.y
      shape = `<path d="M${node.x},${dbY} L${node.x + node.width},${dbY} L${node.x + node.width - 8},${dbY + 8} L${node.x + 8},${dbY + 8} Z" fill="${fillColor}" stroke="${strokeColor}" stroke-width="${strokeWidth}"/>`
      shape += `<path d="M${node.x + 8},${dbY + 8} L${node.x + node.width - 8},${dbY + 8} L${node.x + node.width - 16},${dbY + dbHeight} L${node.x + 16},${dbY + dbHeight} Z" fill="${fillColor}" stroke="${strokeColor}" stroke-width="${strokeWidth}"/>`
      shape += `<ellipse cx="${node.x + node.width / 2}" cy="${dbY + 8}" rx="${node.width / 2 - 8}" ry="4" fill="${fillColor}" stroke="${strokeColor}" stroke-width="${strokeWidth * 0.5}"/>`
      break
    case "server":
      shape = `<rect x="${node.x}" y="${node.y}" width="${node.width}" height="${node.height}" fill="${fillColor}" stroke="${strokeColor}" stroke-width="${strokeWidth}"/>`
      const slots = 3
      const slotHeight = node.height / (slots + 1)
      for (let i = 1; i <= slots; i++) {
        shape += `<line x1="${node.x + 8}" y1="${node.y + i * slotHeight}" x2="${node.x + node.width - 8}" y2="${node.y + i * slotHeight}" stroke="${strokeColor}" stroke-width="${strokeWidth * 0.5}"/>`
      }
      break
    case "cloud":
      shape = `<ellipse cx="${node.x + node.width / 2}" cy="${node.y + node.height / 2}" rx="${node.width / 2}" ry="${node.height / 2}" fill="${fillColor}" stroke="${strokeColor}" stroke-width="${strokeWidth}"/>`
      break
    case "queue":
      shape = `<rect x="${node.x}" y="${node.y}" width="${node.width}" height="${node.height}" rx="8" fill="${fillColor}" stroke="${strokeColor}" stroke-width="${strokeWidth}"/>`
      const arrowX = node.x + node.width / 2
      shape += `<polygon points="${arrowX + 10},${node.y + node.height / 2} ${arrowX},${node.y + node.height / 2 - 6} ${arrowX},${node.y + node.height / 2 + 6}" fill="${strokeColor}"/>`
      break
    default:
      shape = `<rect x="${node.x}" y="${node.y}" width="${node.width}" height="${node.height}" fill="${fillColor}" stroke="${strokeColor}" stroke-width="${strokeWidth}"/>`
  }

  const labelX = node.x + node.width / 2
  const labelY = node.y + node.height + 12

  const label = `<text x="${labelX}" y="${labelY}" text-anchor="middle" font-family="${USPTO.fonts.label}" font-size="${USPTO.fontSizes.label}" fill="${strokeColor}">${escapeXml(node.label)}</text>`

  const refNum =
    patentMode && node.referenceNum
      ? `<text x="${refX}" y="${refY}" font-family="${USPTO.fonts.reference}" font-size="${USPTO.fontSizes.reference}" fill="${strokeColor}">${node.referenceNum}</text>`
      : ""

  return shape + label + refNum
}

function getNodeCenter(node: DiagramNode): { x: number; y: number } {
  return {
    x: node.x + node.width / 2,
    y: node.y + node.height / 2,
  }
}

function getEdgePath(edge: DiagramEdge, nodes: DiagramNode[]): string {
  const fromNode = nodes.find((n) => n.id === edge.from)
  const toNode = nodes.find((n) => n.id === edge.to)

  if (!fromNode || !toNode) return ""

  const from = getNodeCenter(fromNode)
  const to = getNodeCenter(toNode)

  const fromRight = fromNode.x + fromNode.width
  const fromBottom = fromNode.y + fromNode.height
  const toRight = toNode.x + toNode.width
  const toBottom = toNode.y + toNode.height

  let startX = from.x
  let startY = from.y
  let endX = to.x
  let endY = to.y

  if (from.x < to.x && from.y < to.y) {
    startY = fromBottom
    endY = to.y
  } else if (from.x > to.x) {
    if (Math.abs(from.y - to.y) < Math.abs(from.x - to.x) / 2) {
      startX = fromRight
      endX = toNode.x
    }
  }

  const midX = (startX + endX) / 2
  const path = `M${startX},${startY} L${endX},${endY}`

  return path
}

export function renderEdge(edge: DiagramEdge, nodes: DiagramNode[]): string {
  const strokeColor = USPTO.colors.black
  const strokeWidth = edge.type === "dashed" ? 0.5 : 1
  const strokeDasharray = edge.type === "dashed" ? "4,2" : "none"

  const path = getEdgePath(edge, nodes)
  if (!path) return ""

  let svg = `<path d="${path}" fill="none" stroke="${strokeColor}" stroke-width="${strokeWidth}" stroke-dasharray="${strokeDasharray}"/>`

  const fromNode = nodes.find((n) => n.id === edge.from)
  const toNode = nodes.find((n) => n.id === edge.to)
  if (!fromNode || !toNode) return ""

  {
    const to = getNodeCenter(toNode)
    const angle = Math.atan2(to.y - fromNode.y, to.x - fromNode.x)
    const arrowSize = 8
    const arrowX = to.x - (toNode.width / 2) * Math.cos(angle)
    const arrowY = to.y - (toNode.height / 2) * Math.sin(angle)

    const ax1 = arrowX - arrowSize * Math.cos(angle - Math.PI / 6)
    const ay1 = arrowY - arrowSize * Math.sin(angle - Math.PI / 6)
    const ax2 = arrowX - arrowSize * Math.cos(angle + Math.PI / 6)
    const ay2 = arrowY - arrowSize * Math.sin(angle + Math.PI / 6)

    svg += `<polygon points="${arrowX},${arrowY} ${ax1},${ay1} ${ax2},${ay2}" fill="${strokeColor}"/>`
  }

  if (edge.label) {
    const from = getNodeCenter(fromNode)
    const to = getNodeCenter(toNode)
    const midX = (from.x + to.x) / 2
    const midY = (from.y + to.y) / 2
    svg += `<text x="${midX}" y="${midY - 8}" text-anchor="middle" font-family="${USPTO.fonts.label}" font-size="${USPTO.fontSizes.label}" fill="${strokeColor}">${escapeXml(edge.label)}</text>`
  }

  return svg
}

export function renderDiagram(data: DiagramData, options: RenderOptions = {}): string {
  const { patentMode = false, figureNumber, showGrid = false, scale = 1 } = options

  const { width, height } = USPTO.sheet
  const area = getUsableArea()

  let svg = `<?xml version="1.0" encoding="UTF-8"?>`
  svg += `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" width="${width * scale}" height="${height * scale}">`

  svg += `<defs>`
  svg += `<marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">`
  svg += `<polygon points="0 0, 10 3.5, 0 7" fill="${USPTO.colors.black}"/>`
  svg += `</marker>`
  svg += `</defs>`

  if (showGrid) {
    const gridSize = 20
    let grid = ""
    for (let x = area.x; x <= width - USPTO.margins.right; x += gridSize) {
      grid += `<line x1="${x}" y1="${area.y}" x2="${x}" y2="${height - USPTO.margins.bottom}" stroke="#e0e0e0" stroke-width="0.5"/>`
    }
    for (let y = area.y; y <= height - USPTO.margins.bottom; y += gridSize) {
      grid += `<line x1="${area.x}" y1="${y}" x2="${width - USPTO.margins.right}" y2="${y}" stroke="#e0e0e0" stroke-width="0.5"/>`
    }
    svg += `<g id="grid">${grid}</g>`
  }

  svg += `<rect x="0" y="0" width="${width}" height="${height}" fill="white"/>`

  for (const edge of data.edges) {
    svg += renderEdge(edge, data.nodes)
  }

  for (const node of data.nodes) {
    if ("systemType" in node) {
      svg += renderSystemNode(node as SystemNode, options)
    } else {
      svg += renderNode(node, options)
    }
  }

  if (patentMode && figureNumber) {
    svg += `<text x="${width - FIGURE_NUMBER_OFFSET.x}" y="${FIGURE_NUMBER_OFFSET.y}" text-anchor="end" font-family="${USPTO.fonts.primary}" font-size="${USPTO.fontSizes.title}" font-weight="bold">${figureNumber}</text>`
  }

  if (data.title && !patentMode) {
    svg += `<text x="${width / 2}" y="20" text-anchor="middle" font-family="${USPTO.fonts.primary}" font-size="${USPTO.fontSizes.title}">${escapeXml(data.title)}</text>`
  }

  svg += `</svg>`

  return svg
}

function escapeXml(str: string): string {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;")
}

export function svgToDataUrl(svg: string): string {
  const encoded = encodeURIComponent(svg)
  return `data:image/svg+xml;charset=utf-8,${encoded}`
}

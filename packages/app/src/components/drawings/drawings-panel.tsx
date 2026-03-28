import { createSignal, createEffect, For, Show, onMount } from "solid-js"
import { createStore, produce } from "solid-js/store"
import { Button } from "@openpatent/ui/button"
import { Switch } from "@openpatent/ui/switch"
import { USPTO } from "../../templates/uspto-config"
import {
  createFlowchartTemplate,
  type DiagramData,
  type DiagramNode,
  type DiagramEdge,
  autoLayout,
} from "../../templates/flowchart-nodes"
import { createSystemTemplate } from "../../templates/system-nodes"
import { renderDiagram, svgToDataUrl, type RenderOptions } from "../../renderer/render-svg"

export function DrawingsPanel() {
  const [diagram, setDiagram] = createStore<DiagramData>({
    nodes: [],
    edges: [],
  })
  const [patentMode, setPatentMode] = createSignal(false)
  const [figureNumber, setFigureNumber] = createSignal("FIG. 1")
  const [diagramType, setDiagramType] = createSignal<"flowchart" | "system">("flowchart")
  const [selectedNode, setSelectedNode] = createSignal<string | null>(null)
  const [editingLabel, setEditingLabel] = createSignal<string | null>(null)
  const [zoom, setZoom] = createSignal(0.5)
  const [pan, setPan] = createSignal({ x: 0, y: 0 })
  const [showGrid, setShowGrid] = createSignal(true)

  let svgContainer: HTMLDivElement | undefined

  const renderOptions = (): RenderOptions => ({
    patentMode: patentMode(),
    figureNumber: patentMode() ? figureNumber() : undefined,
    showGrid: showGrid(),
    scale: 1,
  })

  const svgContent = () => renderDiagram(diagram, renderOptions())
  const svgUrl = () => svgToDataUrl(svgContent())

  const createNewFlowchart = () => {
    const template = createFlowchartTemplate("New Process")
    setDiagram(template)
  }

  const createNewSystem = () => {
    const template = createSystemTemplate("System Architecture")
    setDiagram(template)
  }

  const autoArrange = () => {
    const arranged = autoLayout(diagram.nodes, diagram.edges)
    setDiagram("nodes", arranged)
  }

  const addNode = (type: "process" | "decision" | "start" | "end" | "input" | "output") => {
    const area = { x: 200, y: 100 + diagram.nodes.length * 80 }
    const newNode: DiagramNode = {
      id: `${type}-${Date.now()}`,
      type,
      label: type.charAt(0).toUpperCase() + type.slice(1),
      x: area.x,
      y: area.y,
      width: type === "decision" ? 80 : 120,
      height: type === "start" || type === "end" ? 40 : 60,
      referenceNum: 100 + diagram.nodes.length,
    }
    setDiagram("nodes", [...diagram.nodes, newNode])
  }

  const deleteSelectedNode = () => {
    const selected = selectedNode()
    if (!selected) return
    setDiagram(
      "nodes",
      diagram.nodes.filter((n) => n.id !== selected),
    )
    setDiagram(
      "edges",
      diagram.edges.filter((e) => e.from !== selected && e.to !== selected),
    )
    setSelectedNode(null)
  }

  const exportSVG = () => {
    const svg = svgContent()
    const blob = new Blob([svg], { type: "image/svg+xml" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `patent-drawing-${figureNumber().replace(/[^0-9a-z]/gi, "-")}.svg`
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleWheel = (e: WheelEvent) => {
    if (e.ctrlKey || e.metaKey) {
      e.preventDefault()
      const delta = e.deltaY > 0 ? -0.1 : 0.1
      setZoom((z) => Math.max(0.2, Math.min(2, z + delta)))
    }
  }

  const handleTypeChange = (e: Event) => {
    const value = (e.target as HTMLSelectElement).value as "flowchart" | "system"
    setDiagramType(value)
    if (value === "flowchart") createNewFlowchart()
    else createNewSystem()
  }

  onMount(() => {
    if (diagram.nodes.length === 0) {
      createNewFlowchart()
    }
  })

  return (
    <div class="flex flex-col h-full overflow-hidden">
      <div class="shrink-0 flex items-center gap-2 px-3 py-2 border-b border-border-weak-base flex-wrap">
        <select
          value={diagramType()}
          onChange={handleTypeChange}
          class="px-2 py-1 text-sm border border-border-weak-base rounded bg-background-default"
        >
          <option value="flowchart">Flowchart</option>
          <option value="system">System</option>
        </select>
        <Button variant="secondary" size="small" onClick={autoArrange}>
          Auto Layout
        </Button>
        <div class="flex-1" />
        <Switch checked={patentMode()} onChange={setPatentMode}>
          Patent Mode
        </Switch>
        <Show when={patentMode()}>
          <input
            type="text"
            value={figureNumber()}
            onInput={(e) => setFigureNumber(e.currentTarget.value)}
            class="w-20 px-2 py-1 text-xs border border-border-weak-base rounded"
            placeholder="FIG. 1"
          />
        </Show>
        <Button variant="secondary" size="small" onClick={exportSVG}>
          Export SVG
        </Button>
      </div>

      <Show when={patentMode()}>
        <div class="shrink-0 flex items-center gap-2 px-3 py-1.5 bg-background-stronger border-b border-border-weak-base text-xs">
          <span class="text-text-weak">Add node:</span>
          <Button variant="ghost" size="small" onClick={() => addNode("process")}>
            Process
          </Button>
          <Button variant="ghost" size="small" onClick={() => addNode("decision")}>
            Decision
          </Button>
          <Button variant="ghost" size="small" onClick={() => addNode("start")}>
            Start
          </Button>
          <Button variant="ghost" size="small" onClick={() => addNode("end")}>
            End
          </Button>
          <Button variant="ghost" size="small" onClick={() => addNode("input")}>
            Input
          </Button>
          <Show when={selectedNode()}>
            <Button variant="ghost" size="small" onClick={deleteSelectedNode} class="text-red-500">
              Delete
            </Button>
          </Show>
        </div>
      </Show>

      <div ref={svgContainer} class="flex-1 overflow-hidden relative bg-background-default" onWheel={handleWheel}>
        <div
          class="absolute inset-0 flex items-center justify-center"
          style={{
            transform: `scale(${zoom()}) translate(${pan().x}px, ${pan().y}px)`,
            "transform-origin": "center center",
          }}
        >
          <Show
            when={svgContent()}
            fallback={<div class="text-text-weak text-sm">Click "Flowchart" or "System" to create a diagram</div>}
          >
            <div
              class="border border-border-weak-base shadow-lg"
              style={{
                width: `${USPTO.sheet.width / 2}px`,
                height: `${USPTO.sheet.height / 2}px`,
              }}
            >
              <img src={svgUrl()} alt="Patent Drawing" class="w-full h-full" style={{ "pointer-events": "none" }} />
            </div>
          </Show>
        </div>

        <div class="absolute bottom-3 right-3 flex items-center gap-2 bg-background-weak px-2 py-1 rounded text-xs">
          <button class="hover:text-text-base px-1" onClick={() => setZoom((z) => Math.max(0.2, z - 0.1))}>
            −
          </button>
          <span>{Math.round(zoom() * 100)}%</span>
          <button class="hover:text-text-base px-1" onClick={() => setZoom((z) => Math.min(2, z + 0.1))}>
            +
          </button>
        </div>
      </div>

      <Show when={selectedNode() && !patentMode()}>
        <div class="shrink-0 p-3 border-t border-border-weak-base bg-background-stronger">
          <div class="text-xs text-text-weak mb-2">Selected Node</div>
          <Show when={editingLabel() === selectedNode()}>
            <input
              type="text"
              value={diagram.nodes.find((n) => n.id === selectedNode())?.label ?? ""}
              onInput={(e) => {
                const node = diagram.nodes.find((n) => n.id === selectedNode())
                if (node) {
                  const idx = diagram.nodes.indexOf(node)
                  setDiagram("nodes", idx, "label", e.currentTarget.value)
                }
              }}
              onBlur={() => setEditingLabel(null)}
              onKeyDown={(e) => e.key === "Enter" && setEditingLabel(null)}
              class="w-full px-2 py-1 text-sm border border-border-weak-base rounded"
              autofocus
            />
          </Show>
          <Show when={editingLabel() !== selectedNode()}>
            <div class="flex items-center gap-2">
              <span class="text-sm">{diagram.nodes.find((n) => n.id === selectedNode())?.label}</span>
              <Button variant="ghost" size="small" onClick={() => setEditingLabel(selectedNode())}>
                Edit
              </Button>
              <Button variant="ghost" size="small" onClick={deleteSelectedNode} class="text-red-500">
                Delete
              </Button>
            </div>
          </Show>
        </div>
      </Show>
    </div>
  )
}

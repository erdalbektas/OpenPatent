import { Component, createSignal, createEffect, onMount, Show, For } from "solid-js"
import { useDialog } from "@openpatent-ai/ui/context/dialog"
import { Dialog } from "@openpatent-ai/ui/dialog"
import { Button } from "@openpatent-ai/ui/button"
import { TextField } from "@openpatent-ai/ui/text-field"
import { Icon } from "@openpatent-ai/ui/icon"
import { Select } from "@openpatent-ai/ui/select"
import { showToast } from "@openpatent-ai/ui/toast"
import { useGlobalSDK } from "@/context/global-sdk"

interface PlannedTask {
  id: number
  agent: string
  task: string
  depends_on: number[]
  expected_output: string
}

interface OrchestrationPlan {
  tasks: PlannedTask[]
  technology: string
  estimated_time: string
  premium_agents_needed: string[]
  local_agents_needed: string[]
}

export const DialogOrchestrator: Component = () => {
  const dialog = useDialog()
  const globalSDK = useGlobalSDK()

  const [step, setStep] = createSignal<"input" | "planning" | "plan" | "executing" | "completed">("input")
  const [userRequest, setUserRequest] = createSignal("")
  const [technology, setTechnology] = createSignal("software")
  const [plan, setPlan] = createSignal<OrchestrationPlan | null>(null)
  const [thinkingLog, setThinkingLog] = createSignal<Array<{ timestamp: string; stage: string; message: string }>>([])
  const [formattedPlan, setFormattedPlan] = createSignal("")
  const [completedTasks, setCompletedTasks] = createSignal<number[]>([])
  const [failedTasks, setFailedTasks] = createSignal<number[]>([])
  const [loading, setLoading] = createSignal(false)

  const technologies = [
    { value: "software", label: "Software" },
    { value: "ai", label: "AI/ML" },
    { value: "biotech", label: "Biotech/Pharma" },
    { value: "mechanics", label: "Mechanics" },
  ]

  const handleCreatePlan = async () => {
    if (!userRequest().trim()) {
      showToast({
        variant: "error",
        title: "Request required",
        description: "Please describe your invention.",
      })
      return
    }

    setLoading(true)
    setStep("planning")

    try {
      const token = localStorage.getItem("access_token")
      const response = await fetch("/api/patent/orchestrator/plan/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token || ""}`,
        },
        body: JSON.stringify({
          request: userRequest(),
          technology: technology(),
        }),
      })

      const data = await response.json()

      if (data.success) {
        setPlan(data.plan)
        setThinkingLog(data.thinking_log || [])
        setFormattedPlan(data.formatted_plan || "")
        setStep("plan")
      } else {
        showToast({
          variant: "error",
          title: "Planning failed",
          description: data.error || "Could not create plan.",
        })
        setStep("input")
      }
    } catch (e) {
      showToast({
        variant: "error",
        title: "Error",
        description: "Failed to connect to server.",
      })
      setStep("input")
    } finally {
      setLoading(false)
    }
  }

  const handleExecutePlan = async () => {
    setStep("executing")
    setCompletedTasks([])
    setFailedTasks([])
    setThinkingLog([])

    try {
      const token = localStorage.getItem("access_token")
      const response = await fetch("/api/patent/orchestrator/execute/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token || ""}`,
        },
        body: JSON.stringify({
          request: userRequest(),
          technology: technology(),
        }),
      })

      const data = await response.json()

      if (data.success) {
        setCompletedTasks(data.completed_tasks || [])
        setFailedTasks(data.failed_tasks || [])
        setThinkingLog(data.thinking_log || [])
        setStep("completed")

        showToast({
          variant: "success",
          icon: "circle-check",
          title: "Execution complete",
          description: `${data.completed_tasks?.length || 0} tasks completed.`,
        })
      } else {
        showToast({
          variant: "error",
          title: "Execution failed",
          description: data.error || "Could not execute plan.",
        })
        setStep("plan")
      }
    } catch (e) {
      showToast({
        variant: "error",
        title: "Error",
        description: "Failed to connect to server.",
      })
      setStep("plan")
    }
  }

  const handleClose = () => {
    dialog.close()
  }

  const getStatusIcon = (taskId: number) => {
    if (completedTasks().includes(taskId)) return "circle-check"
    if (failedTasks().includes(taskId)) return "circle-x"
    return "circle"
  }

  const getStatusColor = (taskId: number) => {
    if (completedTasks().includes(taskId)) return "text-icon-success-base"
    if (failedTasks().includes(taskId)) return "text-icon-critical-base"
    return "text-text-weak"
  }

  const isPremiumAgent = (agent: string) => {
    const premium = ["mock_examiner", "office_action_response", "claim_strategy", "specification_perfection"]
    return premium.includes(agent)
  }

  return (
    <Dialog
      title="Patent Orchestrator"
      description="AI-powered patent drafting assistant"
      action={
        <Show when={step() === "plan"}>
          <Button onClick={handleExecutePlan} variant="primary" icon="play">
            Execute Plan
          </Button>
        </Show>
      }
    >
      <div class="w-[36rem]">
        <Show when={step() === "input"}>
          <div class="flex flex-col gap-4 py-4">
            <div class="text-14-regular text-text-base">
              Describe your invention and the orchestrator will create a detailed plan for drafting your patent.
            </div>

            <TextField label="Technology Type" value={technology()} onChange={setTechnology}>
              <For each={technologies}>{(tech) => <option value={tech.value}>{tech.label}</option>}</For>
            </TextField>

            <div class="flex flex-col gap-1">
              <label class="text-12-medium text-text-strong">Your Request</label>
              <textarea
                class="w-full h-40 p-3 rounded-lg border border-border-weak-base bg-background-base text-14-regular text-text-strong resize-none focus:outline-none focus:border-border-base"
                placeholder="Describe your invention in detail. For example: 'I have invented a new solar panel inverter with integrated battery management that optimizes power conversion efficiency by 15%...'"
                value={userRequest()}
                onInput={(e) => setUserRequest(e.currentTarget.value)}
              />
            </div>

            <Button onClick={handleCreatePlan} variant="primary" icon="sparkles" loading={loading()} class="mt-2">
              Create Plan
            </Button>
          </div>
        </Show>

        <Show when={step() === "planning"}>
          <div class="flex flex-col items-center gap-4 py-12">
            <Icon name="spinner" size="large" class="animate-spin text-icon-brand-base" />
            <div class="text-14-medium text-text-strong">Analyzing your request...</div>
            <div class="text-12-regular text-text-weak text-center max-w-64">
              The orchestrator is breaking down your request into tasks for specialized agents.
            </div>
          </div>
        </Show>

        <Show when={step() === "plan" || step() === "executing" || step() === "completed"}>
          <div class="flex flex-col gap-4 py-4">
            <div class="flex items-center justify-between">
              <div class="text-14-medium text-text-strong">Execution Plan</div>
              <Show when={step() !== "completed"}>
                <Button variant="ghost" size="small" onClick={handleClose}>
                  Cancel
                </Button>
              </Show>
            </div>

            <Show when={formattedPlan()}>
              <div class="p-4 rounded-lg bg-surface-raised-base border border-border-weak-base max-h-64 overflow-y-auto">
                <pre class="text-12-regular text-text-base whitespace-pre-wrap font-sans">{formattedPlan()}</pre>
              </div>
            </Show>

            <Show when={step() === "executing"}>
              <div class="text-14-medium text-text-strong mt-2">Execution Progress</div>
              <div class="flex flex-col gap-2 max-h-48 overflow-y-auto">
                <For each={plan()?.tasks || []}>
                  {(task) => (
                    <div class="flex items-center gap-3 p-2 rounded-lg border border-border-weak-base">
                      <Icon name={getStatusIcon(task.id)} size="small" class={getStatusColor(task.id)} />
                      <div class="flex-1 min-w-0">
                        <div class="text-12-medium text-text-strong truncate">{task.task}</div>
                        <div class="text-10-regular text-text-weak flex items-center gap-1">
                          <span>{isPremiumAgent(task.agent) ? "🔒 Premium" : "📝 Local"}</span>
                          <Show when={task.depends_on.length > 0}>
                            <span>• Depends on {task.depends_on.join(", ")}</span>
                          </Show>
                        </div>
                      </div>
                    </div>
                  )}
                </For>
              </div>
            </Show>

            <Show when={step() === "completed"}>
              <div class="flex flex-col gap-4 mt-4">
                <div class="flex items-center gap-2 p-3 rounded-lg bg-surface-success-base border border-border-success-base">
                  <Icon name="circle-check" size="medium" class="text-icon-success-base" />
                  <div>
                    <div class="text-14-medium text-text-strong">Execution Complete</div>
                    <div class="text-12-regular text-text-weak">
                      {completedTasks().length} completed, {failedTasks().length} failed
                    </div>
                  </div>
                </div>

                <Show when={failedTasks().length > 0}>
                  <div class="flex items-center gap-2 p-3 rounded-lg bg-surface-critical-base border border-border-critical-base">
                    <Icon name="circle-x" size="medium" class="text-icon-critical-base" />
                    <div>
                      <div class="text-14-medium text-text-strong">Failed Tasks</div>
                      <div class="text-12-regular text-text-weak">
                        Some tasks failed. Check the thinking log for details.
                      </div>
                    </div>
                  </div>
                </Show>
              </div>
            </Show>
          </div>
        </Show>
      </div>
    </Dialog>
  )
}

export const openOrchestrator = () => {
  const dialog = useDialog()
  dialog.show(() => <DialogOrchestrator />)
}

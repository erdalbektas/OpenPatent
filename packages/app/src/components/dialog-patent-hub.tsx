import { Component, createSignal, onMount, Show, For } from "solid-js"
import { useDialog } from "@openpatent-ai/ui/context/dialog"
import { Dialog } from "@openpatent-ai/ui/dialog"
import { Button } from "@openpatent-ai/ui/button"
import { TextField } from "@openpatent-ai/ui/text-field"
import { Icon } from "@openpatent-ai/ui/icon"
import { TabGroup, TabList, Tab, TabPanel } from "@openpatent-ai/ui/tabs"
import { showToast } from "@openpatent-ai/ui/toast"
import { useGlobalSDK } from "@/context/global-sdk"
import { DialogOrchestrator } from "./dialog-orchestrator"

interface PatentSession {
  id: string
  title: string
  status: string
  invention_title: string
  technical_field: string
  created_at: string
  updated_at: string
}

interface QuotaStatus {
  tier: string
  reset_date: string
  quotas: {
    mock_examiner: { used: number; limit: number; remaining: number }
    office_action_response: { used: number; limit: number; remaining: number }
    claim_strategy: { used: number; limit: number; remaining: number }
    specification_perfection: { used: number; limit: number; remaining: number }
  }
}

export const DialogPatentHub: Component = () => {
  const dialog = useDialog()
  const globalSDK = useGlobalSDK()

  const [activeTab, setActiveTab] = createSignal("sessions")
  const [sessions, setSessions] = createSignal<PatentSession[]>([])
  const [quota, setQuota] = createSignal<QuotaStatus | null>(null)
  const [loading, setLoading] = createSignal(true)
  const [newSessionTitle, setNewSessionTitle] = createSignal("")

  onMount(async () => {
    await loadPatentData()
  })

  const loadPatentData = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem("access_token")

      const [sessionsRes, quotaRes] = await Promise.all([
        fetch("/api/patent/sessions/", {
          headers: { Authorization: `Bearer ${token || ""}` },
        }),
        fetch("/api/patent/quota/", {
          headers: { Authorization: `Bearer ${token || ""}` },
        }),
      ])

      if (sessionsRes.ok) {
        const data = await sessionsRes.json()
        setSessions(data.sessions || [])
      }

      if (quotaRes.ok) {
        const data = await quotaRes.json()
        setQuota(data)
      }
    } catch (e) {
      console.error("Failed to load patent data:", e)
    } finally {
      setLoading(false)
    }
  }

  const createSession = async () => {
    if (!newSessionTitle().trim()) return

    try {
      const token = localStorage.getItem("access_token")
      const res = await fetch("/api/patent/sessions/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token || ""}`,
        },
        body: JSON.stringify({ title: newSessionTitle() }),
      })

      if (res.ok) {
        const session = await res.json()
        setSessions([session, ...sessions()])
        setNewSessionTitle("")
        showToast({
          variant: "success",
          icon: "circle-check",
          title: "Session created",
          description: "Your patent drafting session is ready.",
        })
      }
    } catch (e) {
      showToast({
        variant: "error",
        icon: "circle-ban-sign",
        title: "Failed to create session",
      })
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "drafting":
        return "text-text-weak"
      case "review":
        return "text-text-base"
      case "perfecting":
        return "text-text-strong"
      case "filed":
        return "text-icon-success-base"
      case "examining":
        return "text-icon-warning-base"
      default:
        return "text-text-weak"
    }
  }

  return (
    <Dialog
      title="Patent Hub"
      description="Manage your patent drafting and prosecution"
      action={<Button onClick={() => dialog.close()}>Done</Button>}
    >
      <div class="w-[32rem]">
        <TabGroup value={activeTab()} onChange={setActiveTab}>
          <TabList>
            <Tab value="sessions">
              <Icon name="document" size="small" />
              Sessions
            </Tab>
            <Tab value="agents">
              <Icon name="bot" size="small" />
              Agents
            </Tab>
            <Tab value="quota">
              <Icon name="chart-bar" size="small" />
              Quota
            </Tab>
          </TabList>

          <TabPanel value="sessions">
            <div class="flex flex-col gap-4 py-4">
              <div class="flex gap-2">
                <TextField
                  placeholder="New patent session title..."
                  value={newSessionTitle()}
                  onInput={(e) => setNewSessionTitle(e.currentTarget.value)}
                  class="flex-1"
                />
                <Button onClick={createSession} icon="plus-small">
                  Create
                </Button>
              </div>

              <div class="p-4 rounded-lg bg-surface-raised-base border border-border-weak-base">
                <div class="flex items-center gap-3">
                  <Icon name="sparkles" size="medium" class="text-icon-brand-base" />
                  <div class="flex-1">
                    <div class="text-14-medium text-text-strong">AI Patent Orchestrator</div>
                    <div class="text-12-regular text-text-weak">
                      Describe your invention and let AI create a complete patent drafting plan
                    </div>
                  </div>
                  <Button onClick={() => dialog.show(() => <DialogOrchestrator />)} icon="wand">
                    Start
                  </Button>
                </div>
              </div>

              <Show when={!loading()}>
                <Show when={sessions().length > 0}>
                  <div class="flex flex-col gap-2">
                    <For each={sessions()}>
                      {(session) => (
                        <button
                          class="flex items-center justify-between p-3 rounded-lg border border-border-weak-base hover:border-border-base hover:bg-surface-raised-base-hover transition-colors text-left"
                          onClick={() => dialog.show(() => <DialogPatentSession session={session} />)}
                        >
                          <div class="flex-1 min-w-0">
                            <div class="text-14-medium text-text-strong truncate">{session.title}</div>
                            <div class="text-12-regular text-text-weak">
                              {session.invention_title || "No invention title"} •{" "}
                              {session.technical_field || "No field"}
                            </div>
                          </div>
                          <div class="flex items-center gap-2">
                            <span class={`text-12-medium ${getStatusColor(session.status)}`}>{session.status}</span>
                            <Icon name="chevron-right" size="small" class="text-icon-weak" />
                          </div>
                        </button>
                      )}
                    </For>
                  </div>
                </Show>
                <Show when={sessions().length === 0}>
                  <div class="text-14-regular text-text-weak text-center py-8">
                    No patent sessions yet. Create your first session to get started.
                  </div>
                </Show>
              </Show>

              <Show when={loading()}>
                <div class="flex items-center justify-center py-8">
                  <Icon name="spinner" size="large" class="animate-spin" />
                </div>
              </Show>
            </div>
          </TabPanel>

          <TabPanel value="agents">
            <div class="flex flex-col gap-4 py-4">
              <div class="text-14-medium text-text-strong">Free Agents (Local)</div>
              <div class="flex flex-col gap-2">
                <For
                  each={[
                    { id: "invention_disclosure", name: "Invention Disclosure", desc: "Analyze invention ideas" },
                    { id: "patent_drafter", name: "Patent Drafter", desc: "Draft claims and specification" },
                    { id: "prior_art_searcher", name: "Prior Art Searcher", desc: "Prepare search queries" },
                    { id: "technical_drafter", name: "Technical Drawing", desc: "Create drawing descriptions" },
                  ]}
                >
                  {(agent) => (
                    <div class="flex items-center gap-3 p-3 rounded-lg border border-border-weak-base">
                      <Icon name="bot" size="small" class="text-icon-base" />
                      <div class="flex-1">
                        <div class="text-14-medium text-text-strong">{agent.name}</div>
                        <div class="text-12-regular text-text-weak">{agent.desc}</div>
                      </div>
                      <span class="text-12-medium text-text-success-base">Free</span>
                    </div>
                  )}
                </For>
              </div>

              <div class="pt-4 border-t border-border-weak-base">
                <div class="text-14-medium text-text-strong mb-2">Premium Agents (Server)</div>
                <div class="flex flex-col gap-2">
                  <For
                    each={[
                      { id: "mock_examiner", name: "Mock Examiner", desc: "Pre-filing review", premium: true },
                      {
                        id: "office_action_response",
                        name: "Office Action Response",
                        desc: "Respond to USPTO",
                        premium: true,
                      },
                      {
                        id: "claim_strategy",
                        name: "Claim Strategy",
                        desc: "Amend claims strategically",
                        premium: true,
                      },
                      {
                        id: "specification_perfection",
                        name: "Specification Perfection",
                        desc: "Improve specifications",
                        premium: true,
                      },
                    ]}
                  >
                    {(agent) => (
                      <div class="flex items-center gap-3 p-3 rounded-lg border border-border-weak-base">
                        <Icon name="sparkles" size="small" class="text-icon-warning-base" />
                        <div class="flex-1">
                          <div class="text-14-medium text-text-strong">{agent.name}</div>
                          <div class="text-12-regular text-text-weak">{agent.desc}</div>
                        </div>
                        <span class="text-12-medium text-text-warning-base">Premium</span>
                      </div>
                    )}
                  </For>
                </div>
              </div>
            </div>
          </TabPanel>

          <TabPanel value="quota">
            <div class="flex flex-col gap-4 py-4">
              <Show when={quota()}>
                <div class="flex items-center justify-between p-3 rounded-lg bg-surface-raised-base">
                  <div>
                    <div class="text-14-medium text-text-strong">Current Plan</div>
                    <div class="text-12-regular text-text-weak capitalize">{quota()?.tier}</div>
                  </div>
                  <Button variant="secondary" size="small" onClick={() => dialog.show(() => <DialogPremium />)}>
                    Upgrade
                  </Button>
                </div>

                <div class="space-y-3">
                  <For each={Object.entries(quota()?.quotas || {})}>
                    {([key, data]) => (
                      <div class="p-3 rounded-lg border border-border-weak-base">
                        <div class="flex items-center justify-between mb-2">
                          <span class="text-14-medium text-text-strong capitalize">{key.replace(/_/g, " ")}</span>
                          <span class="text-12-regular text-text-weak">
                            {data.used} / {data.limit}
                          </span>
                        </div>
                        <div class="h-2 rounded-full bg-surface-raised-base overflow-hidden">
                          <div
                            class="h-full bg-icon-brand-base transition-all"
                            style={{ width: `${(data.used / data.limit) * 100}%` }}
                          />
                        </div>
                        <div class="text-12-regular text-text-weak mt-1">{data.remaining} remaining this month</div>
                      </div>
                    )}
                  </For>
                </div>

                <div class="text-12-regular text-text-weak text-center pt-2">
                  Resets {new Date(quota()!.reset_date).toLocaleDateString()}
                </div>
              </Show>
            </div>
          </TabPanel>
        </TabGroup>
      </div>
    </Dialog>
  )
}

import { DialogPremium } from "./dialog-settings"

const DialogPatentSession: Component<{ session: PatentSession }> = (props) => {
  const dialog = useDialog()

  return (
    <Dialog title={props.session.title} action={<Button onClick={() => dialog.close()}>Close</Button>}>
      <div class="w-[28rem] flex flex-col gap-4 py-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <div class="text-12-medium text-text-weak">Status</div>
            <div class="text-14-regular text-text-strong capitalize">{props.session.status}</div>
          </div>
          <div>
            <div class="text-12-medium text-text-weak">Invention</div>
            <div class="text-14-regular text-text-strong truncate">{props.session.invention_title || "Not set"}</div>
          </div>
          <div>
            <div class="text-12-medium text-text-weak">Technical Field</div>
            <div class="text-14-regular text-text-strong">{props.session.technical_field || "Not set"}</div>
          </div>
          <div>
            <div class="text-12-medium text-text-weak">Last Updated</div>
            <div class="text-14-regular text-text-strong">
              {new Date(props.session.updated_at).toLocaleDateString()}
            </div>
          </div>
        </div>

        <div class="pt-4 border-t border-border-weak-base">
          <div class="text-14-medium text-text-strong mb-2">Quick Actions</div>
          <div class="flex flex-col gap-2">
            <Button variant="secondary" icon="document">
              Edit Claims
            </Button>
            <Button variant="secondary" icon="document-text">
              Edit Specification
            </Button>
            <Show when={props.session.status === "drafting"}>
              <Button icon="sparkles" onClick={() => dialog.show(() => <DialogPremium />)}>
                Run Mock Examiner (Premium)
              </Button>
            </Show>
          </div>
        </div>
      </div>
    </Dialog>
  )
}

import { Component, createSignal, onCleanup, onMount, Show, For } from "solid-js"
import { useDialog } from "@openpatent-ai/ui/context/dialog"
import { Dialog } from "@openpatent-ai/ui/dialog"
import { Button } from "@openpatent-ai/ui/button"
import { TextField } from "@openpatent-ai/ui/text-field"
import { Icon } from "@openpatent-ai/ui/icon"
import { Switch } from "@openpatent-ai/ui/switch"
import { TabGroup, TabList, Tab, TabPanel } from "@openpatent-ai/ui/tabs"
import { showToast } from "@openpatent-ai/ui/toast"
import { DialogPatentHub } from "../../../app/src/components/dialog-patent-hub"

export const DialogSettings: Component = () => {
  const dialog = useDialog()
  const [activeTab, setActiveTab] = createSignal("general")
  const [serverUrl, setServerUrl] = createSignal("")
  const [autoUpdate, setAutoUpdate] = createSignal(true)
  const [betaUpdates, setBetaUpdates] = createSignal(false)

  onMount(() => {
    const storedUrl = localStorage.getItem("openpatent_server_url")
    const storedAutoUpdate = localStorage.getItem("openpatent_auto_update")
    const storedBetaUpdates = localStorage.getItem("openpatent_beta_updates")

    if (storedUrl) setServerUrl(storedUrl)
    if (storedAutoUpdate !== null) setAutoUpdate(storedAutoUpdate === "true")
    if (storedBetaUpdates !== null) setBetaUpdates(storedBetaUpdates === "true")

    const handleOpenSettings = () => dialog.show(() => <DialogSettings />)
    const handleOpenAgents = () => dialog.show(() => <DialogAgents />)
    const handleOpenPremium = () => dialog.show(() => <DialogPremium />)
    const handleOpenPatentHub = () => dialog.show(() => <DialogPatentHub />)

    window.addEventListener("open-settings", handleOpenSettings)
    window.addEventListener("open-agents", handleOpenAgents)
    window.addEventListener("open-premium", handleOpenPremium)
    window.addEventListener("open-patent-hub", handleOpenPatentHub)

    onCleanup(() => {
      window.removeEventListener("open-settings", handleOpenSettings)
      window.removeEventListener("open-agents", handleOpenAgents)
      window.removeEventListener("open-premium", handleOpenPremium)
      window.removeEventListener("open-patent-hub", handleOpenPatentHub)
    })
  })

  const handleSave = () => {
    localStorage.setItem("openpatent_server_url", serverUrl())
    localStorage.setItem("openpatent_auto_update", String(autoUpdate()))
    localStorage.setItem("openpatent_beta_updates", String(betaUpdates()))
    dialog.close()
  }

  const handleOpenAgents = () => {
    dialog.show(() => <DialogAgents />)
  }

  const handleOpenPremium = () => {
    dialog.show(() => <DialogPremium />)
  }

  const handleOpenPatentHub = () => {
    dialog.show(() => <DialogPatentHub />)
  }

  return (
    <Dialog
      title="Settings"
      description="Configure OpenPatent preferences"
      action={
        <Button onClick={handleSave} variant="primary">
          Save
        </Button>
      }
    >
      <div class="w-96">
        <TabGroup value={activeTab()} onChange={setActiveTab}>
          <TabList>
            <Tab value="general">
              <Icon name="settings" size="small" />
              General
            </Tab>
            <Tab value="providers">
              <Icon name="cloud" size="small" />
              Providers
            </Tab>
            <Tab value="agents">
              <Icon name="bot" size="small" />
              Agents
            </Tab>
            <Tab value="premium">
              <Icon name="star" size="small" />
              Premium
            </Tab>
          </TabList>

          <TabPanel value="general">
            <div class="flex flex-col gap-4 py-4">
              <TextField
                label="Server URL"
                placeholder="http://localhost:8000"
                value={serverUrl()}
                onInput={(e) => setServerUrl(e.currentTarget.value)}
              />

              <div class="flex items-center justify-between">
                <div>
                  <div class="text-14-medium text-text-strong">Auto-update</div>
                  <div class="text-12-regular text-text-weak">Automatically check for updates</div>
                </div>
                <Switch checked={autoUpdate()} onChange={setAutoUpdate} />
              </div>

              <div class="flex items-center justify-between">
                <div>
                  <div class="text-14-medium text-text-strong">Beta updates</div>
                  <div class="text-12-regular text-text-weak">Receive beta releases</div>
                </div>
                <Switch checked={betaUpdates()} onChange={setBetaUpdates} />
              </div>

              <div class="pt-4 border-t border-border-weak-base">
                <Button variant="secondary" icon="document" onClick={handleOpenPatentHub} class="w-full">
                  Open Patent Hub
                </Button>
                <div class="text-12-regular text-text-weak mt-2 text-center">
                  Manage patent drafting sessions and premium agents
                </div>
              </div>
            </div>
          </TabPanel>

          <TabPanel value="providers">
            <div class="flex flex-col gap-4 py-4">
              <div class="text-14-regular text-text-base">Connect AI providers to use models in OpenPatent.</div>

              <div class="flex flex-col gap-2">
                <button
                  class="flex items-center gap-3 p-3 rounded-lg border border-border-weak-base hover:border-border-base hover:bg-surface-raised-base-hover transition-colors text-left"
                  onClick={handleOpenProviders}
                >
                  <Icon name="cloud" size="medium" class="text-icon-base" />
                  <div class="flex-1">
                    <div class="text-14-medium text-text-strong">Cloud Providers</div>
                    <div class="text-12-regular text-text-weak">OpenAI, Anthropic, Google, Qwen, MiniMax</div>
                  </div>
                  <Icon name="chevron-right" size="small" class="text-icon-weak" />
                </button>

                <button
                  class="flex items-center gap-3 p-3 rounded-lg border border-border-weak-base hover:border-border-base hover:bg-surface-raised-base-hover transition-colors text-left"
                  onClick={handleOpenProviders}
                >
                  <Icon name="desktop" size="medium" class="text-icon-base" />
                  <div class="flex-1">
                    <div class="text-14-medium text-text-strong">Local Providers</div>
                    <div class="text-12-regular text-text-weak">LM Studio, Ollama, and OpenAI-compatible servers</div>
                  </div>
                  <Icon name="chevron-right" size="small" class="text-icon-weak" />
                </button>

                <button
                  class="flex items-center gap-3 p-3 rounded-lg border border-border-weak-base hover:border-border-base hover:bg-surface-raised-base-hover transition-colors text-left"
                  onClick={handleOpenProviders}
                >
                  <Icon name="server" size="medium" class="text-icon-base" />
                  <div class="flex-1">
                    <div class="text-14-medium text-text-strong">OpenPatent Server</div>
                    <div class="text-12-regular text-text-weak">Use hosted API with your subscription</div>
                  </div>
                  <Icon name="chevron-right" size="small" class="text-icon-weak" />
                </button>
              </div>

              <Button onClick={handleOpenProviders} icon="settings" variant="secondary">
                Manage Providers
              </Button>
            </div>
          </TabPanel>

          <TabPanel value="agents">
            <div class="flex flex-col gap-4 py-4">
              <div class="text-14-regular text-text-base">Manage your custom agents for advanced AI interactions.</div>
              <Button onClick={handleOpenAgents} icon="plus-small">
                Manage Agents
              </Button>
            </div>
          </TabPanel>

          <TabPanel value="premium">
            <div class="flex flex-col gap-4 py-4">
              <div class="text-14-regular text-text-base">Unlock advanced features with OpenPatent Premium.</div>
              <Button onClick={handleOpenPremium} icon="star">
                View Premium Plans
              </Button>
            </div>
          </TabPanel>
        </TabGroup>
      </div>
    </Dialog>
  )
}

export const DialogProviders: Component = () => {
  const dialog = useDialog()
  const [cloudProviders, setCloudProviders] = createSignal<string[]>([])
  const [localProviders, setLocalProviders] = createSignal<Array<{ name: string; type: string; base_url: string }>>([])
  const [loading, setLoading] = createSignal(true)

  onMount(async () => {
    await loadProviders()
  })

  const loadProviders = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem("access_token")

      const [cloudRes, localRes] = await Promise.all([
        fetch("/api/providers/credentials/", {
          headers: { Authorization: `Bearer ${token || ""}` },
        }),
        fetch("/api/providers/local/", {
          headers: { Authorization: `Bearer ${token || ""}` },
        }),
      ])

      if (cloudRes.ok) {
        const data = await cloudRes.json()
        setCloudProviders(data.providers || [])
      }

      if (localRes.ok) {
        const data = await localRes.json()
        setLocalProviders(data.local_providers || [])
      }
    } catch (e) {
      console.error("Failed to load providers:", e)
    } finally {
      setLoading(false)
    }
  }

  const handleRemoveCloudProvider = async (provider: string) => {
    try {
      const token = localStorage.getItem("access_token")
      const res = await fetch(`/api/providers/credentials/?provider=${provider}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token || ""}` },
      })

      if (res.ok) {
        setCloudProviders(cloudProviders().filter((p) => p !== provider))
        showToast({
          variant: "success",
          icon: "circle-check",
          title: "Provider removed",
          description: `${provider} has been disconnected.`,
        })
      }
    } catch (e) {
      showToast({
        variant: "error",
        icon: "circle-ban-sign",
        title: "Failed to remove provider",
      })
    }
  }

  const handleRemoveLocalProvider = async (name: string) => {
    try {
      const token = localStorage.getItem("access_token")
      const res = await fetch(`/api/providers/local/?name=${encodeURIComponent(name)}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token || ""}` },
      })

      if (res.ok) {
        setLocalProviders(localProviders().filter((p) => p.name !== name))
        showToast({
          variant: "success",
          icon: "circle-check",
          title: "Provider removed",
          description: `${name} has been disconnected.`,
        })
      }
    } catch (e) {
      showToast({
        variant: "error",
        icon: "circle-ban-sign",
        title: "Failed to remove provider",
      })
    }
  }

  return (
    <Dialog
      title="Providers"
      description="Manage your AI providers"
      action={<Button onClick={() => dialog.close()}>Done</Button>}
    >
      <div class="w-[32rem] max-h-96 overflow-y-auto">
        <div class="flex flex-col gap-6 py-4">
          <Show when={!loading()}>
            <div>
              <div class="text-14-medium text-text-strong mb-2">Cloud Providers</div>
              <div class="flex flex-col gap-2">
                <Show when={cloudProviders().length === 0}>
                  <div class="text-14-regular text-text-weak text-center py-4">
                    No cloud providers connected. Add one to get started.
                  </div>
                </Show>
                <For each={cloudProviders()}>
                  {(provider) => (
                    <div class="flex items-center justify-between p-3 rounded-lg border border-border-weak-base">
                      <div class="flex items-center gap-2">
                        <Icon name="cloud" size="small" class="text-icon-base" />
                        <span class="text-14-medium text-text-strong capitalize">{provider}</span>
                      </div>
                      <Button variant="ghost" size="small" onClick={() => handleRemoveCloudProvider(provider)}>
                        <Icon name="trash" size="small" />
                      </Button>
                    </div>
                  )}
                </For>
                <Button
                  variant="secondary"
                  icon="plus-small"
                  onClick={() => dialog.show(() => <DialogConnectProviderNew />)}
                >
                  Add Cloud Provider
                </Button>
              </div>
            </div>

            <div>
              <div class="text-14-medium text-text-strong mb-2">Local Providers</div>
              <div class="flex flex-col gap-2">
                <Show when={localProviders().length === 0}>
                  <div class="text-14-regular text-text-weak text-center py-4">
                    No local providers configured. Add one to use local models.
                  </div>
                </Show>
                <For each={localProviders()}>
                  {(provider) => (
                    <div class="flex items-center justify-between p-3 rounded-lg border border-border-weak-base">
                      <div class="flex items-center gap-2">
                        <Icon name="desktop" size="small" class="text-icon-base" />
                        <div>
                          <div class="text-14-medium text-text-strong">{provider.name}</div>
                          <div class="text-12-regular text-text-weak truncate max-w-48">{provider.base_url}</div>
                        </div>
                      </div>
                      <Button variant="ghost" size="small" onClick={() => handleRemoveLocalProvider(provider.name)}>
                        <Icon name="trash" size="small" />
                      </Button>
                    </div>
                  )}
                </For>
                <Button
                  variant="secondary"
                  icon="plus-small"
                  onClick={() => dialog.show(() => <DialogConnectProviderNew />)}
                >
                  Add Local Provider
                </Button>
              </div>
            </div>
          </Show>

          <Show when={loading()}>
            <div class="flex items-center justify-center py-8">
              <Icon name="spinner" size="large" class="animate-spin" />
            </div>
          </Show>
        </div>
      </div>
    </Dialog>
  )
}

import { DialogConnectProviderNew } from "../../../app/src/components/dialog-connect-provider-new"

export const DialogAgents: Component = () => {
  const dialog = useDialog()
  const [agents, setAgents] = createSignal<
    Array<{
      id: string
      name: string
      description: string
      agent_type: string
      category: string
      system_prompt: string
      allowed_modes: string[]
      color: string
      tags: string[]
    }>
  >([])
  const [editingAgent, setEditingAgent] = createSignal<{
    id: string
    name: string
    description: string
    agent_type: string
    category: string
    system_prompt: string
    allowed_modes: string[]
    color: string
    tags: string[]
  } | null>(null)
  const [loading, setLoading] = createSignal(true)
  const [serverUrl, setServerUrl] = createSignal("")

  onMount(async () => {
    const storedUrl = localStorage.getItem("openpatent_server_url")
    if (storedUrl) setServerUrl(storedUrl)

    const storedAgents = localStorage.getItem("openpatent_agents")
    if (storedAgents) {
      setAgents(JSON.parse(storedAgents))
    }

    const handleOpenAgents = () => dialog.show(() => <DialogAgents />)
    window.addEventListener("open-agents", handleOpenAgents)

    await syncWithServer()

    onCleanup(() => window.removeEventListener("open-agents", handleOpenAgents))
  })

  const syncWithServer = async () => {
    const token = localStorage.getItem("access_token")
    if (!token) {
      setLoading(false)
      return
    }

    try {
      const res = await fetch("/api/patent/agents/", {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (res.ok) {
        const data = await res.json()
        if (data.agents && data.agents.length > 0) {
          const serverAgents = data.agents.map((a: any) => ({
            id: a.id,
            name: a.name,
            description: a.description,
            agent_type: a.type,
            category: a.category,
            system_prompt: a.system_prompt || "",
            allowed_modes: a.allowed_modes || ["chat"],
            color: a.color || "#3B82F6",
            tags: a.tags || [],
          }))
          setAgents(serverAgents)
        }
      }
    } catch (e) {
      console.error("Failed to sync agents with server:", e)
    } finally {
      setLoading(false)
    }
  }

  const handleSaveAgents = (
    newAgents: Array<{
      id: string
      name: string
      description: string
      agent_type: string
      category: string
      system_prompt: string
      allowed_modes: string[]
      color: string
      tags: string[]
    }>,
  ) => {
    setAgents(newAgents)
    localStorage.setItem("openpatent_agents", JSON.stringify(newAgents))
  }

  const handleAddAgent = () => {
    setEditingAgent({
      id: `agent_${crypto.randomUUID().slice(0, 8)}`,
      name: "",
      description: "",
      agent_type: "local",
      category: "custom",
      system_prompt: "",
      allowed_modes: ["chat"],
      color: "#3B82F6",
      tags: [],
    })
  }

  const handleEditAgent = (agent: {
    id: string
    name: string
    description: string
    agent_type: string
    category: string
    system_prompt: string
    allowed_modes: string[]
    color: string
    tags: string[]
  }) => {
    setEditingAgent(agent)
  }

  const handleDeleteAgent = (agentId: string) => {
    const newAgents = agents().filter((a) => a.id !== agentId)
    handleSaveAgents(newAgents)
  }

  const handleSaveAgent = async (agent: {
    id: string
    name: string
    description: string
    agent_type: string
    category: string
    system_prompt: string
    allowed_modes: string[]
    color: string
    tags: string[]
  }) => {
    const existingIndex = agents().findIndex((a) => a.id === agent.id)
    let newAgents = agents()

    if (existingIndex >= 0) {
      newAgents = [...agents()]
      newAgents[existingIndex] = agent
    } else {
      newAgents = [...agents(), agent]
    }

    handleSaveAgents(newAgents)

    const token = localStorage.getItem("access_token")
    if (token) {
      try {
        const res = await fetch("/api/patent/agents/create/", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(agent),
        })

        if (!res.ok) {
          showToast({
            variant: "error",
            icon: "circle-ban-sign",
            title: "Failed to sync with server",
          })
        }
      } catch (e) {
        console.error("Failed to sync agent with server:", e)
      }
    }

    setEditingAgent(null)
  }

  const handleCancelEdit = () => {
    setEditingAgent(null)
  }

  return (
    <Dialog
      title="Agents"
      description="Manage your custom AI agents"
      action={
        <Button onClick={() => dialog.close()} variant="secondary">
          Close
        </Button>
      }
    >
      <div class="w-[36rem] max-h-[32rem] overflow-y-auto">
        <Show when={loading()}>
          <div class="flex items-center justify-center py-8">
            <Icon name="spinner" size="large" class="animate-spin" />
          </div>
        </Show>

        <Show when={!loading() && !editingAgent()}>
          <div class="flex flex-col gap-3 py-4">
            <Show when={agents().length === 0}>
              <div class="text-14-regular text-text-weak text-center py-8">
                No custom agents yet. Create your first agent to get started.
              </div>
            </Show>

            <For each={agents()}>
              {(agent) => (
                <div class="flex items-center justify-between p-3 rounded-lg border border-border-weak-base hover:border-border-base">
                  <div class="flex items-center gap-3">
                    <div
                      class="w-8 h-8 rounded-full flex items-center justify-center text-white text-12-bold"
                      style={{ "background-color": agent.color }}
                    >
                      {agent.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div class="text-14-medium text-text-strong">{agent.name}</div>
                      <div class="text-12-regular text-text-weak">{agent.description}</div>
                      <div class="flex items-center gap-2 mt-1">
                        <span class="text-10-medium text-text-weak px-2 py-0.5 rounded bg-surface-raised-base border border-border-weak-base">
                          {agent.category}
                        </span>
                        <span class="text-10-medium text-text-weak px-2 py-0.5 rounded bg-surface-raised-base border border-border-weak-base capitalize">
                          {agent.agent_type}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div class="flex items-center gap-2">
                    <Button variant="ghost" size="small" onClick={() => handleEditAgent(agent)}>
                      <Icon name="pencil" size="small" />
                    </Button>
                    <Button variant="ghost" size="small" onClick={() => handleDeleteAgent(agent.id)}>
                      <Icon name="trash" size="small" />
                    </Button>
                  </div>
                </div>
              )}
            </For>

            <Button onClick={handleAddAgent} icon="plus-small" class="mt-2">
              Add Agent
            </Button>
          </div>
        </Show>

        <Show when={editingAgent()}>
          <AgentEditor agent={editingAgent()!} onSave={handleSaveAgent} onCancel={handleCancelEdit} />
        </Show>
      </div>
    </Dialog>
  )
}

const AgentEditor: Component<{
  agent: {
    id: string
    name: string
    description: string
    agent_type: string
    category: string
    system_prompt: string
    allowed_modes: string[]
    color: string
    tags: string[]
  }
  onSave: (agent: {
    id: string
    name: string
    description: string
    agent_type: string
    category: string
    system_prompt: string
    allowed_modes: string[]
    color: string
    tags: string[]
  }) => void
  onCancel: () => void
}> = (props) => {
  const [name, setName] = createSignal(props.agent.name)
  const [description, setDescription] = createSignal(props.agent.description)
  const [agentType, setAgentType] = createSignal(props.agent.agent_type)
  const [category, setCategory] = createSignal(props.agent.category)
  const [systemPrompt, setSystemPrompt] = createSignal(props.agent.system_prompt)
  const [allowedModes, setAllowedModes] = createSignal(props.agent.allowed_modes || [])
  const [color, setColor] = createSignal(props.agent.color || "#3B82F6")
  const [tags, setTags] = createSignal(props.agent.tags || [])
  const [newTag, setNewTag] = createSignal("")

  const categories = [
    { value: "drafting", label: "Drafting" },
    { value: "review", label: "Review" },
    { value: "analysis", label: "Analysis" },
    { value: "perfecting", label: "Perfecting" },
    { value: "response", label: "Response" },
    { value: "strategy", label: "Strategy" },
    { value: "orchestrator", label: "Orchestrator" },
    { value: "custom", label: "Custom" },
  ]

  const modes = ["chat", "edit", "ask", "agent"]

  const colors = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#06B6D4", "#84CC16"]

  const handleAddTag = () => {
    if (newTag() && !tags().includes(newTag())) {
      setTags([...tags(), newTag()])
      setNewTag("")
    }
  }

  const handleRemoveTag = (tag: string) => {
    setTags(tags().filter((t) => t !== tag))
  }

  const handleToggleMode = (mode: string) => {
    if (allowedModes().includes(mode)) {
      setAllowedModes(allowedModes().filter((m) => m !== mode))
    } else {
      setAllowedModes([...allowedModes(), mode])
    }
  }

  return (
    <div class="flex flex-col gap-4 py-4">
      <div class="flex items-center gap-4">
        <div class="flex flex-col gap-1 flex-1">
          <label class="text-12-medium text-text-strong">Agent Name</label>
          <TextField
            placeholder="My Custom Agent"
            value={name()}
            onInput={(e) => setName(e.currentTarget.value)}
            autofocus
          />
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-12-medium text-text-strong">Color</label>
          <div class="flex gap-1">
            <For each={colors}>
              {(c) => (
                <button
                  type="button"
                  class={`w-8 h-8 rounded-full transition-transform ${
                    color() === c ? "scale-110 ring-2 ring-offset-1 ring-border-base" : ""
                  }`}
                  style={{ "background-color": c }}
                  onClick={() => setColor(c)}
                />
              )}
            </For>
          </div>
        </div>
      </div>

      <TextField
        label="Description"
        placeholder="What this agent does"
        value={description()}
        onInput={(e) => setDescription(e.currentTarget.value)}
      />

      <div class="flex gap-4">
        <div class="flex flex-col gap-1 flex-1">
          <label class="text-12-medium text-text-strong">Type</label>
          <select
            class="w-full p-2 rounded-lg border border-border-weak-base bg-background-base text-14-regular text-text-strong focus:outline-none focus:border-border-base"
            value={agentType()}
            onChange={(e) => setAgentType(e.currentTarget.value)}
          >
            <option value="local">Local</option>
            <option value="premium">Premium</option>
          </select>
        </div>

        <div class="flex flex-col gap-1 flex-1">
          <label class="text-12-medium text-text-strong">Category</label>
          <select
            class="w-full p-2 rounded-lg border border-border-weak-base bg-background-base text-14-regular text-text-strong focus:outline-none focus:border-border-base"
            value={category()}
            onChange={(e) => setCategory(e.currentTarget.value)}
          >
            <For each={categories}>{(cat) => <option value={cat.value}>{cat.label}</option>}</For>
          </select>
        </div>
      </div>

      <div class="flex flex-col gap-1">
        <label class="text-12-medium text-text-strong">Allowed Modes</label>
        <div class="flex gap-2">
          <For each={modes}>
            {(mode) => (
              <button
                type="button"
                class={`px-3 py-1 rounded-lg text-12-medium border transition-colors ${
                  allowedModes().includes(mode)
                    ? "bg-surface-raised-base-hover border-border-base text-text-strong"
                    : "bg-background-base border-border-weak-base text-text-weak hover:border-border-base"
                }`}
                onClick={() => handleToggleMode(mode)}
              >
                {mode}
              </button>
            )}
          </For>
        </div>
      </div>

      <div class="flex flex-col gap-1">
        <label class="text-12-medium text-text-strong">System Prompt</label>
        <textarea
          class="w-full h-40 p-3 rounded-lg border border-border-weak-base bg-background-base text-14-regular text-text-strong resize-none focus:outline-none focus:border-border-base"
          placeholder="You are a helpful coding assistant that..."
          value={systemPrompt()}
          onInput={(e) => setSystemPrompt(e.currentTarget.value)}
        />
      </div>

      <div class="flex flex-col gap-1">
        <label class="text-12-medium text-text-strong">Tags</label>
        <div class="flex gap-2">
          <TextField
            placeholder="Add a tag"
            value={newTag()}
            onInput={(e) => setNewTag(e.currentTarget.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAddTag()}
          />
          <Button variant="secondary" onClick={handleAddTag}>
            Add
          </Button>
        </div>
        <div class="flex flex-wrap gap-1 mt-2">
          <For each={tags()}>
            {(tag) => (
              <span class="flex items-center gap-1 px-2 py-1 rounded bg-surface-raised-base border border-border-weak-base text-12-regular text-text-strong">
                {tag}
                <button type="button" onClick={() => handleRemoveTag(tag)} class="hover:text-text-danger">
                  <Icon name="x-small" size="small" />
                </button>
              </span>
            )}
          </For>
        </div>
      </div>

      <div class="flex justify-end gap-2 pt-2 border-t border-border-weak-base">
        <Button variant="secondary" onClick={props.onCancel}>
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={() =>
            props.onSave({
              id: props.agent.id,
              name: name(),
              description: description(),
              agent_type: agentType(),
              category: category(),
              system_prompt: systemPrompt(),
              allowed_modes: allowedModes(),
              color: color(),
              tags: tags(),
            })
          }
          disabled={!name() || !systemPrompt()}
        >
          Save
        </Button>
      </div>
    </div>
  )
}

export const DialogPremium: Component = () => {
  const dialog = useDialog()
  const platform = (window as any).__openpatent__?.platform === "tauri" ? (window as any).__openpatent__ : null

  const handleOpenLink = () => {
    if (platform?.openLink) {
      platform.openLink("https://openpatent.ai/premium")
    } else {
      window.open("https://openpatent.ai/premium", "_blank")
    }
    dialog.close()
  }

  onMount(() => {
    const handleOpenPremium = () => dialog.show(() => <DialogPremium />)
    window.addEventListener("open-premium", handleOpenPremium)
    onCleanup(() => window.removeEventListener("open-premium", handleOpenPremium))
  })

  return (
    <Dialog
      title="OpenPatent Premium"
      description="Unlock advanced features"
      action={
        <Button onClick={() => dialog.close()} variant="secondary">
          Close
        </Button>
      }
    >
      <div class="w-96">
        <div class="flex flex-col gap-6 py-4">
          <div class="text-center">
            <div class="text-24-bold text-text-strong mb-2">Upgrade to Premium</div>
            <div class="text-14-regular text-text-weak">
              Get access to advanced agents, higher limits, and priority support.
            </div>
          </div>

          <div class="flex flex-col gap-3">
            <div class="flex items-center gap-3 p-3 rounded-lg border border-border-weak-base">
              <Icon name="bot" size="large" class="text-icon-base" />
              <div>
                <div class="text-14-medium text-text-strong">Advanced Agents</div>
                <div class="text-12-regular text-text-weak">Create and manage custom AI agents</div>
              </div>
            </div>

            <div class="flex items-center gap-3 p-3 rounded-lg border border-border-weak-base">
              <Icon name="lightning" size="large" class="text-icon-base" />
              <div>
                <div class="text-14-medium text-text-strong">Higher Limits</div>
                <div class="text-12-regular text-text-weak">5M tokens/hour vs 100K for free</div>
              </div>
            </div>

            <div class="flex items-center gap-3 p-3 rounded-lg border border-border-weak-base">
              <Icon name="priority" size="large" class="text-icon-base" />
              <div>
                <div class="text-14-medium text-text-strong">Priority Support</div>
                <div class="text-12-regular text-text-weak">Get help from our team faster</div>
              </div>
            </div>
          </div>

          <Button onClick={handleOpenLink} variant="primary" icon="external-link">
            View Plans & Pricing
          </Button>
        </div>
      </div>
    </Dialog>
  )
}

import { createSignal, createResource, Resource } from "solid-js"

export interface Agent {
  id: string
  name: string
  description: string
  systemPrompt: string
  model?: {
    providerID: string
    modelID: string
  }
  tools?: Record<string, boolean>
  maxSteps?: number
  temperature?: number
  topP?: number
  permission?: {
    edit: string
    bash: Record<string, string>
    skill: Record<string, string>
  }
}

export interface AgentStore {
  agents: Agent[]
  loading: boolean
  error: string | null
}

const API_URL =
  (typeof window !== "undefined" ? localStorage.getItem("openpatent_server_url") : null) || "http://localhost:8000"

async function getAuthHeaders(): Promise<HeadersInit> {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null
  return token
    ? { Authorization: `Bearer ${token}`, "Content-Type": "application/json" }
    : { "Content-Type": "application/json" }
}

export async function fetchAgents(): Promise<Agent[]> {
  try {
    const headers = await getAuthHeaders()
    const response = await fetch(`${API_URL}/api/agents/`, { headers })

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Authentication required")
      }
      throw new Error("Failed to fetch agents")
    }

    return response.json()
  } catch (error) {
    console.error("Failed to fetch agents:", error)
    return []
  }
}

export async function createAgent(agent: Omit<Agent, "id">): Promise<Agent | null> {
  try {
    const headers = await getAuthHeaders()
    const response = await fetch(`${API_URL}/api/agents/`, {
      method: "POST",
      headers,
      body: JSON.stringify(agent),
    })

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Authentication required")
      }
      throw new Error("Failed to create agent")
    }

    return response.json()
  } catch (error) {
    console.error("Failed to create agent:", error)
    return null
  }
}

export async function updateAgent(agent: Agent): Promise<Agent | null> {
  try {
    const headers = await getAuthHeaders()
    const response = await fetch(`${API_URL}/api/agents/${agent.id}/`, {
      method: "PUT",
      headers,
      body: JSON.stringify(agent),
    })

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Authentication required")
      }
      throw new Error("Failed to update agent")
    }

    return response.json()
  } catch (error) {
    console.error("Failed to update agent:", error)
    return null
  }
}

export async function deleteAgent(agentId: string): Promise<boolean> {
  try {
    const headers = await getAuthHeaders()
    const response = await fetch(`${API_URL}/api/agents/${agentId}/`, {
      method: "DELETE",
      headers,
    })

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Authentication required")
      }
      throw new Error("Failed to delete agent")
    }

    return true
  } catch (error) {
    console.error("Failed to delete agent:", error)
    return false
  }
}

export function useAgents(): {
  agents: Resource<Agent[]>
  loading: () => boolean
  error: () => string | null
  refresh: () => void
} {
  const [agents, { refetch }] = createResource<Agent[]>(fetchAgents)

  return {
    agents,
    loading: () => agents.loading,
    error: () => agents.error ?? null,
    refresh: refetch,
  }
}

export function createAgentStore() {
  const [store, setStore] = createSignal<AgentStore>({
    agents: [],
    loading: false,
    error: null,
  })

  const loadAgents = async () => {
    setStore((s) => ({ ...s, loading: true, error: null }))
    try {
      const agents = await fetchAgents()
      setStore((s) => ({ ...s, agents, loading: false }))
    } catch (error) {
      setStore((s) => ({
        ...s,
        loading: false,
        error: error instanceof Error ? error.message : "Failed to load agents",
      }))
    }
  }

  const addAgent = async (agent: Omit<Agent, "id">) => {
    const newAgent = await createAgent(agent)
    if (newAgent) {
      setStore((s) => ({
        ...s,
        agents: [...s.agents, newAgent],
      }))
    }
    return newAgent
  }

  const updateAgentInStore = async (agent: Agent) => {
    const updated = await updateAgent(agent)
    if (updated) {
      setStore((s) => ({
        ...s,
        agents: s.agents.map((a) => (a.id === agent.id ? updated : a)),
      }))
    }
    return updated
  }

  const removeAgent = async (agentId: string) => {
    const success = await deleteAgent(agentId)
    if (success) {
      setStore((s) => ({
        ...s,
        agents: s.agents.filter((a) => a.id !== agentId),
      }))
    }
    return success
  }

  return {
    store,
    loadAgents,
    addAgent,
    updateAgent: updateAgentInStore,
    removeAgent,
  }
}

export function useAgentAPI() {
  const { store, loadAgents, addAgent, updateAgent, removeAgent } = createAgentStore()

  return {
    agents: () => store().agents,
    loading: () => store().loading,
    error: () => store().error,
    loadAgents,
    addAgent,
    updateAgent,
    removeAgent,
  }
}

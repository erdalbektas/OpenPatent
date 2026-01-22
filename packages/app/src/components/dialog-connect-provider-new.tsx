import { Component, createSignal, Show, For } from "solid-js"
import { useDialog } from "@openpatent-ai/ui/context/dialog"
import { Dialog } from "@openpatent-ai/ui/dialog"
import { Button } from "@openpatent-ai/ui/button"
import { TextField } from "@openpatent-ai/ui/text-field"
import { Icon } from "@openpatent-ai/ui/icon"
import { showToast } from "@openpatent-ai/ui/toast"
import { useGlobalSDK } from "@/context/global-sdk"

type ProviderType = "openai" | "anthropic" | "google" | "qwen" | "minimax" | "lm-studio" | "ollama"

interface ProviderConfig {
  id: ProviderType
  name: string
  description: string
  apiKeyLabel: string
  apiKeyPlaceholder: string
  requiresApiKey: boolean
  defaultBaseUrl?: string
}

const CLOUD_PROVIDERS: ProviderConfig[] = [
  {
    id: "openai",
    name: "OpenAI",
    description: "GPT-4, GPT-4o, and more",
    apiKeyLabel: "OpenAI API Key",
    apiKeyPlaceholder: "sk-...",
    requiresApiKey: true,
  },
  {
    id: "anthropic",
    name: "Anthropic",
    description: "Claude 3.5, Claude 3, and more",
    apiKeyLabel: "Anthropic API Key",
    apiKeyPlaceholder: "sk-ant-...",
    requiresApiKey: true,
  },
  {
    id: "google",
    name: "Google",
    description: "Gemini 1.5 Pro, Flash, and more",
    apiKeyLabel: "Google AI API Key",
    apiKeyPlaceholder: "AIza...",
    requiresApiKey: true,
  },
  {
    id: "qwen",
    name: "Qwen (Alibaba)",
    description: "Qwen 2.5, Qwen Plus, and more",
    apiKeyLabel: "Qwen API Key",
    apiKeyPlaceholder: "sk-...",
    requiresApiKey: true,
  },
  {
    id: "minimax",
    name: "MiniMax",
    description: "ABAB 6.5s, ABAB 6, and more",
    apiKeyLabel: "MiniMax API Key",
    apiKeyPlaceholder: "...",
    requiresApiKey: true,
  },
]

const LOCAL_PROVIDERS: ProviderConfig[] = [
  {
    id: "lm-studio",
    name: "LM Studio",
    description: "Local models via LM Studio",
    apiKeyLabel: "API Key (optional)",
    apiKeyPlaceholder: "Leave empty for no auth",
    requiresApiKey: false,
    defaultBaseUrl: "http://localhost:1234/v1",
  },
  {
    id: "ollama",
    name: "Ollama",
    description: "Local models via Ollama",
    apiKeyLabel: "API Key (optional)",
    apiKeyPlaceholder: "Leave empty for no auth",
    requiresApiKey: false,
    defaultBaseUrl: "http://localhost:11434",
  },
]

export const DialogConnectProviderNew: Component = () => {
  const dialog = useDialog()
  const globalSDK = useGlobalSDK()

  const [step, setStep] = createSignal<"select" | "configure">("select")
  const [providerType, setProviderType] = createSignal<"cloud" | "local">("cloud")
  const [selectedProvider, setSelectedProvider] = createSignal<ProviderConfig | null>(null)
  const [apiKey, setApiKey] = createSignal("")
  const [baseUrl, setBaseUrl] = createSignal("")
  const [loading, setLoading] = createSignal(false)
  const [error, setError] = createSignal<string | null>(null)

  const handleSelectProvider = (provider: ProviderConfig, type: "cloud" | "local") => {
    setSelectedProvider(provider)
    setProviderType(type)
    setBaseUrl(provider.defaultBaseUrl || "")
    setApiKey("")
    setError(null)
    setStep("configure")
  }

  const handleConnect = async () => {
    if (!selectedProvider()) return

    setLoading(true)
    setError(null)

    try {
      if (providerType() === "cloud") {
        if (!apiKey().trim()) {
          setError("API key is required")
          setLoading(false)
          return
        }

        const response = await fetch("/api/providers/credentials/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
          },
          body: JSON.stringify({
            provider: selectedProvider()!.id,
            api_key: apiKey(),
          }),
        })

        if (!response.ok) {
          const data = await response.json()
          throw new Error(data.error || "Failed to store API key")
        }

        await globalSDK.client.auth.set({
          providerID: selectedProvider()!.id,
          auth: { type: "api", key: apiKey() },
        })
      } else {
        if (!baseUrl().trim()) {
          setError("Server URL is required")
          setLoading(false)
          return
        }

        const response = await fetch("/api/providers/local/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
          },
          body: JSON.stringify({
            type: selectedProvider()!.id,
            name: selectedProvider()!.name,
            base_url: baseUrl(),
            api_key: apiKey(),
          }),
        })

        if (!response.ok) {
          const data = await response.json()
          throw new Error(data.error || "Failed to add local provider")
        }
      }

      showToast({
        variant: "success",
        icon: "circle-check",
        title: `${selectedProvider()!.name} connected`,
        description: `${selectedProvider()!.name} models are now available.`,
      })

      dialog.close()
    } catch (e) {
      setError(e instanceof Error ? e.message : "Connection failed")
    } finally {
      setLoading(false)
    }
  }

  const handleBack = () => {
    if (step() === "configure") {
      setStep("select")
      setSelectedProvider(null)
      setError(null)
    } else {
      dialog.close()
    }
  }

  return (
    <Dialog
      title={step() === "configure" ? `Connect ${selectedProvider()?.name}` : "Connect Provider"}
      action={
        step() === "configure" ? (
          <Button onClick={handleConnect} variant="primary" loading={loading()}>
            Connect
          </Button>
        ) : undefined
      }
    >
      <div class="w-[28rem]">
        <Show when={step() === "select"}>
          <div class="flex flex-col gap-6 py-2">
            <div>
              <div class="text-14-medium text-text-strong mb-2">Cloud Providers</div>
              <div class="flex flex-col gap-2">
                <For each={CLOUD_PROVIDERS}>
                  {(provider) => (
                    <button
                      class="flex items-center gap-3 p-3 rounded-lg border border-border-weak-base hover:border-border-base hover:bg-surface-raised-base-hover transition-colors text-left"
                      onClick={() => handleSelectProvider(provider, "cloud")}
                    >
                      <Icon name="cloud" size="medium" class="text-icon-base" />
                      <div class="flex-1">
                        <div class="text-14-medium text-text-strong">{provider.name}</div>
                        <div class="text-12-regular text-text-weak">{provider.description}</div>
                      </div>
                      <Icon name="chevron-right" size="small" class="text-icon-weak" />
                    </button>
                  )}
                </For>
              </div>
            </div>

            <div>
              <div class="text-14-medium text-text-strong mb-2">Local Providers</div>
              <div class="flex flex-col gap-2">
                <For each={LOCAL_PROVIDERS}>
                  {(provider) => (
                    <button
                      class="flex items-center gap-3 p-3 rounded-lg border border-border-weak-base hover:border-border-base hover:bg-surface-raised-base-hover transition-colors text-left"
                      onClick={() => handleSelectProvider(provider, "local")}
                    >
                      <Icon name="desktop" size="medium" class="text-icon-base" />
                      <div class="flex-1">
                        <div class="text-14-medium text-text-strong">{provider.name}</div>
                        <div class="text-12-regular text-text-weak">{provider.description}</div>
                      </div>
                      <Icon name="chevron-right" size="small" class="text-icon-weak" />
                    </button>
                  )}
                </For>
              </div>
            </div>

            <div class="pt-2 border-t border-border-weak-base">
              <button
                class="flex items-center gap-3 p-3 rounded-lg border border-dashed border-border-weak-base hover:border-border-base hover:bg-surface-raised-base-hover transition-colors text-left w-full"
                onClick={() => dialog.show(() => <DialogUseopenpatentServer />)}
              >
                <Icon name="server" size="medium" class="text-icon-base" />
                <div class="flex-1">
                  <div class="text-14-medium text-text-strong">OpenPatent Server</div>
                  <div class="text-12-regular text-text-weak">Use OpenPatent hosted API (subscription required)</div>
                </div>
              </button>
            </div>
          </div>
        </Show>

        <Show when={step() === "configure" && selectedProvider()}>
          <div class="flex flex-col gap-4 py-2">
            <div class="text-14-regular text-text-base">
              {providerType() === "cloud"
                ? `Enter your ${selectedProvider()!.name} API key to connect your account.`
                : `Configure your ${selectedProvider()!.name} server URL.`}
            </div>

            {providerType() === "local" && (
              <TextField
                label="Server URL"
                placeholder="http://localhost:1234/v1"
                value={baseUrl()}
                onInput={(e) => setBaseUrl(e.currentTarget.value)}
                autofocus={!selectedProvider()!.defaultBaseUrl}
              />
            )}

            {selectedProvider()!.requiresApiKey || providerType() === "cloud" ? (
              <TextField
                label={selectedProvider()!.apiKeyLabel}
                placeholder={selectedProvider()!.apiKeyPlaceholder}
                type="password"
                value={apiKey()}
                onInput={(e) => setApiKey(e.currentTarget.value)}
                autofocus={providerType() === "cloud"}
              />
            ) : (
              <TextField
                label={selectedProvider()!.apiKeyLabel}
                placeholder={selectedProvider()!.apiKeyPlaceholder}
                type="password"
                value={apiKey()}
                onInput={(e) => setApiKey(e.currentTarget.value)}
              />
            )}

            <Show when={error()}>
              <div class="text-14-regular text-text-critical-base p-3 rounded-lg bg-surface-critical-base border border-border-critical-base">
                {error()}
              </div>
            </Show>

            <div class="flex gap-2 pt-2">
              <Button variant="secondary" onClick={handleBack}>
                Back
              </Button>
              <Button variant="primary" onClick={handleConnect} loading={loading()} disabled={loading()}>
                Connect
              </Button>
            </div>
          </div>
        </Show>
      </div>
    </Dialog>
  )
}

const DialogUseopenpatentServer: Component = () => {
  const dialog = useDialog()
  const globalSDK = useGlobalSDK()

  const handleUseServer = async () => {
    try {
      await globalSDK.client.global.dispose()
      showToast({
        variant: "success",
        icon: "circle-check",
        title: "Using OpenPatent Server",
        description: "Connected to OpenPatent hosted API.",
      })
      dialog.close()
    } catch (e) {
      showToast({
        variant: "error",
        icon: "circle-ban-sign",
        title: "Connection failed",
        description: "Could not connect to openpatent server.",
      })
    }
  }

  return (
    <Dialog title="OpenPatent Server" action={<Button onClick={handleUseServer}>Connect</Button>}>
      <div class="flex flex-col gap-4 py-2">
        <div class="text-14-regular text-text-base">
          Use OpenPatent access premium's hosted API to models with your subscription.
        </div>
        <div class="flex flex-col gap-2">
          <div class="flex items-center gap-2 text-14-regular">
            <Icon name="check" size="small" class="text-icon-success-base" />
            <span>Access to Claude, GPT, Gemini, and more</span>
          </div>
          <div class="flex items-center gap-2 text-14-regular">
            <Icon name="check" size="small" class="text-icon-success-base" />
            <span>Automatic rate limiting and quota management</span>
          </div>
          <div class="flex items-center gap-2 text-14-regular">
            <Icon name="check" size="small" class="text-icon-success-base" />
            <span>Priority support and updates</span>
          </div>
        </div>
      </div>
    </Dialog>
  )
}

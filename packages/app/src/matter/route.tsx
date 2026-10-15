import { createResource, For, Show } from "solid-js"
import { ScrollView } from "@opencode/ui/scroll-view"
import { useServerCtx } from "@/runtime/server/runtime"
import { useLayout } from "@/shell/state/layout"
import { useServers } from "@/runtime/server/registry"
import { ServerConnection } from "@/runtime/server/registry"
import { OpenPatentConfig, MATTER_PATHS } from "@openpatent/patent"
import type { ServerApi } from "@/runtime/server/api"

async function readProjectFile(api: ServerApi, directory: string, rel: string) {
  try {
    const bytes = await api.file.read({ path: rel, location: { directory } })
    return new TextDecoder().decode(bytes)
  } catch {
    return null
  }
}

async function loadMatterSummary(api: ServerApi, projectDirectory: string) {
  const configText = await readProjectFile(api, projectDirectory, MATTER_PATHS.config)
  if (!configText) return { isMatter: false as const }

  const config = OpenPatentConfig.parse(JSON.parse(configText))
  const claimsText = (await readProjectFile(api, projectDirectory, MATTER_PATHS.claims)) ?? ""
  const refsText = await readProjectFile(api, projectDirectory, MATTER_PATHS.references)
  const inventionText = await readProjectFile(api, projectDirectory, MATTER_PATHS.invention)

  return {
    isMatter: true as const,
    config,
    gates: {
      disclosure: Boolean(inventionText?.trim()),
      references: Boolean(refsText?.trim()),
      claims: Boolean(claimsText.trim()),
    },
    claimsPreview: claimsText.split("\n").slice(0, 10).join("\n"),
  }
}

export function MatterRoute() {
  const layout = useLayout()
  const servers = useServers()
  const server = () =>
    servers.visible.find((conn) => ServerConnection.key(conn) === layout.home.selection().server) ?? servers.visible[0]

  const serverCtx = useServerCtx(server)
  const directory = () => layout.home.selection().directory

  const [summary] = createResource(
    () => {
      const ctx = serverCtx()
      const dir = directory()
      if (!ctx || !dir) return null
      return { api: ctx.sdk.api, dir }
    },
    async (input) => {
      if (!input) return { isMatter: false as const }
      return loadMatterSummary(input.api, input.dir)
    },
  )

  return (
    <div
      data-slot="matter-panel"
      class="mx-[var(--shell-inline-inset,8px)] mb-[var(--shell-bottom-inset,8px)] mt-[var(--shell-top-inset,8px)] flex min-h-0 flex-1 flex-col self-stretch overflow-hidden rounded-[10px] bg-v2-background-bg-base p-6 shadow-[var(--v2-elevation-raised)]"
    >
      <h1 class="text-lg font-semibold text-v2-text-text-primary">Patent matter</h1>
      <Show when={summary()?.isMatter} fallback={<p class="mt-4 text-v2-text-text-secondary">Select a project with openpatent.json or run openpatent init.</p>}>
        {(data) => (
          <ScrollView class="mt-4 min-h-0 flex-1">
            <p class="text-v2-text-text-secondary">{data().config?.title} · {data().config?.jurisdiction}</p>
            <ul class="mt-4 space-y-2 text-sm">
              <For each={Object.entries(data().gates ?? {})}>
                {([gate, ok]) => (
                  <li class="flex gap-2">
                    <span>{ok ? "✓" : "○"}</span>
                    <span>{gate}</span>
                  </li>
                )}
              </For>
            </ul>
            <pre class="mt-6 whitespace-pre-wrap rounded-md bg-v2-background-bg-surface p-3 text-xs">{data().claimsPreview}</pre>
          </ScrollView>
        )}
      </Show>
    </div>
  )
}

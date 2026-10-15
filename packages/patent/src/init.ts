import path from "node:path"
import { MATTER_PATHS, type Jurisdiction } from "./matter"

export type InitOptions = {
  title: string
  jurisdiction?: Jurisdiction
  docketId?: string
}

const TEMPLATE_OPENCODE = {
  $schema: "https://opencode.ai/config.json",
  default_agent: "counsel",
  plugins: ["@openpatent/plugin"],
  agents: {
    counsel: { mode: "primary" },
  },
} as const

export async function initMatter(targetDir: string, options: InitOptions) {
  const root = path.resolve(targetDir)
  await Bun.write(path.join(root, MATTER_PATHS.config), JSON.stringify({
    title: options.title,
    jurisdiction: options.jurisdiction ?? "USPTO",
    docketId: options.docketId,
  }, null, 2) + "\n")

  const dirs = [
    "disclosure",
    "claims",
    "specification",
    "figures",
    "references",
    "prosecution",
    ".opencode/agents",
    ".opencode/skills",
  ]
  for (const d of dirs) {
    await Bun.write(path.join(root, d, ".gitkeep"), "")
  }

  await Bun.write(
    path.join(root, MATTER_PATHS.invention),
    `# ${options.title}\n\nDescribe the invention, problem solved, and key embodiments.\n`,
  )
  await Bun.write(path.join(root, MATTER_PATHS.questions), "# Open questions\n\n")
  await Bun.write(path.join(root, MATTER_PATHS.claims), "1. \n")
  await Bun.write(path.join(root, MATTER_PATHS.specification), "# Specification\n\n")
  await Bun.write(path.join(root, MATTER_PATHS.numerals), JSON.stringify({ figures: [] }, null, 2) + "\n")
  await Bun.write(path.join(root, MATTER_PATHS.references), JSON.stringify({ references: [] }, null, 2) + "\n")
  await Bun.write(path.join(root, MATTER_PATHS.glossary), "{}\n")
  await Bun.write(path.join(root, MATTER_PATHS.status), JSON.stringify({ phase: "intake", updatedAt: new Date().toISOString() }, null, 2) + "\n")

  await Bun.write(path.join(root, "opencode.jsonc"), JSON.stringify(TEMPLATE_OPENCODE, null, 2) + "\n")
  await Bun.write(path.join(root, "AGENTS.md"), matterAgentsMd())

  return root
}

function matterAgentsMd() {
  return `# OpenPatent matter

This directory is an OpenPatent matter. Use the **counsel** agent to run the drafting workflow.

Keep invention text in \`disclosure/invention.md\`, claims in \`claims/claims.md\`, and run \`patent_lint\` before filing drafts.
`
}

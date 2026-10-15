import path from "node:path"
import {
  chartFromClaimSet,
  exportApplicationMarkdown,
  findNumeralDrift,
  formatGlossary,
  ingestDisclosureFile,
  lintClaims,
  matterPath,
  matterStatusFromFiles,
  mergeGlossary,
  parseClaims,
  parseGlossary,
  readConfig,
  resolveSearchProvider,
  SearchNotConfiguredError,
  NumeralsFile,
} from "@openpatent/patent"
type PatentToolEditor = {
  add: (tool: {
    name: string
    description: string
    input: { type: "object"; properties: Record<string, unknown>; additionalProperties: false }
    options: { codemode: boolean }
    execute: (
      input: unknown,
      ctx: { directory: string },
    ) => Promise<{ output: unknown; content: string }>
  }) => void
}

function matterCwd(directory: string) {
  return path.resolve(directory)
}

async function readMatterFile(cwd: string, key: Parameters<typeof matterPath>[1]) {
  const file = Bun.file(matterPath(cwd, key))
  if (!(await file.exists())) return null
  return await file.text()
}

export function registerPatentTools(editor: PatentToolEditor) {
  const jsonInput = (props: Record<string, unknown>) => ({
    type: "object" as const,
    properties: props,
    additionalProperties: false,
  })

  editor.add({
    name: "patent_matter_status",
    description: "Report which OpenPatent matter workflow gates have content on disk.",
    input: jsonInput({}),
    options: { codemode: false },
    execute: async (_input, ctx) => {
      const cwd = matterCwd(ctx.directory)
      const gates = await matterStatusFromFiles(cwd)
      const content = JSON.stringify(gates, null, 2)
      return { output: gates, content }
    },
  })

  editor.add({
    name: "patent_parse_claims",
    description: "Parse claims/claims.md into structured claim objects.",
    input: jsonInput({}),
    options: { codemode: false },
    execute: async (_input, ctx) => {
      const cwd = matterCwd(ctx.directory)
      const text = (await readMatterFile(cwd, "claims")) ?? ""
      const parsed = parseClaims(text)
      const content = JSON.stringify(parsed, null, 2)
      return { output: parsed, content }
    },
  })

  editor.add({
    name: "patent_lint",
    description: "Lint claims for antecedent basis, indefiniteness, and jurisdiction rules.",
    input: jsonInput({}),
    options: { codemode: false },
    execute: async (_input, ctx) => {
      const cwd = matterCwd(ctx.directory)
      const config = await readConfig(cwd)
      const text = (await readMatterFile(cwd, "claims")) ?? ""
      const result = lintClaims(text, { jurisdiction: config?.jurisdiction })
      const statusPath = matterPath(cwd, "status")
      const status = JSON.parse((await readMatterFile(cwd, "status")) ?? "{}")
      status.lint = { clean: result.clean, errorCount: result.issues.filter((i) => i.severity === "error").length }
      status.updatedAt = new Date().toISOString()
      await Bun.write(statusPath, JSON.stringify(status, null, 2) + "\n")
      const content = JSON.stringify(result, null, 2)
      return { output: result, content }
    },
  })

  editor.add({
    name: "patent_glossary",
    description: "Read or update glossary.json term definitions.",
    input: jsonInput({
      action: { type: "string", enum: ["read", "update"] },
      terms: { type: "object", additionalProperties: { type: "string" } },
    }),
    options: { codemode: false },
    execute: async (input, ctx) => {
      const cwd = matterCwd(ctx.directory)
      const action = (input as { action: string }).action
      const file = matterPath(cwd, "glossary")
      const current = parseGlossary((await readMatterFile(cwd, "glossary")) ?? "{}")
      if (action === "read") {
        const content = formatGlossary(current)
        return { output: current, content }
      }
      const terms = (input as { terms?: Record<string, string> }).terms ?? {}
      const merged = mergeGlossary(current, terms)
      await Bun.write(file, formatGlossary(merged))
      const content = formatGlossary(merged)
      return { output: merged, content }
    },
  })

  editor.add({
    name: "patent_search",
    description: "Search USPTO PatentsView when PATENTSVIEW_API_KEY is configured.",
    input: jsonInput({ query: { type: "string" }, limit: { type: "number" } }),
    options: { codemode: false },
    execute: async (input, ctx) => {
      const query = (input as { query: string }).query
      const limit = (input as { limit?: number }).limit
      try {
        const provider = resolveSearchProvider(process.env)
        const result = await provider.search(query, { limit })
        const content = JSON.stringify(result, null, 2)
        return { output: result, content }
      } catch (err) {
        if (err instanceof SearchNotConfiguredError) {
          return { output: { error: err.message }, content: err.message }
        }
        throw err
      }
    },
  })

  editor.add({
    name: "patent_chart",
    description: "Build element-to-reference chart using word_overlap similarity (baseline, not embeddings).",
    input: jsonInput({
      referenceId: { type: "string" },
      referenceText: { type: "string" },
    }),
    options: { codemode: false },
    execute: async (input, ctx) => {
      const cwd = matterCwd(ctx.directory)
      const claimsText = (await readMatterFile(cwd, "claims")) ?? ""
      const { referenceId, referenceText } = input as { referenceId: string; referenceText: string }
      const charts = chartFromClaimSet(claimsText, referenceId, referenceText)
      const refPath = matterPath(cwd, "references")
      let index = { references: [] as unknown[] }
      try {
        index = JSON.parse((await readMatterFile(cwd, "references")) ?? '{"references":[]}')
      } catch {
        /* empty */
      }
      const entry = { referenceId, charts, method: "word_overlap" }
      const refs = Array.isArray((index as { references: unknown[] }).references)
        ? (index as { references: unknown[] }).references
        : []
      refs.push(entry)
      await Bun.write(refPath, JSON.stringify({ references: refs }, null, 2) + "\n")
      const content = JSON.stringify(charts, null, 2)
      return { output: charts, content }
    },
  })

  editor.add({
    name: "patent_ingest",
    description: "Ingest a text or markdown disclosure file into disclosure/invention.md.",
    input: jsonInput({ sourcePath: { type: "string" } }),
    options: { codemode: false },
    execute: async (input, ctx) => {
      const cwd = matterCwd(ctx.directory)
      const { sourcePath } = input as { sourcePath: string }
      const result = await ingestDisclosureFile(cwd, sourcePath)
      const content = JSON.stringify(result, null, 2)
      return { output: result, content }
    },
  })

  editor.add({
    name: "patent_export",
    description: "Export a single markdown application bundle from matter files.",
    input: jsonInput({}),
    options: { codemode: false },
    execute: async (_input, ctx) => {
      const cwd = matterCwd(ctx.directory)
      const md = await exportApplicationMarkdown(cwd)
      const dest = path.join(cwd, "final_export", "application.md")
      await Bun.write(dest, md)
      return { output: { path: dest }, content: md }
    },
  })

  editor.add({
    name: "patent_numerals",
    description: "Detect reference numeral drift between specification and figures/numerals.json.",
    input: jsonInput({}),
    options: { codemode: false },
    execute: async (_input, ctx) => {
      const cwd = matterCwd(ctx.directory)
      const spec = (await readMatterFile(cwd, "specification")) ?? ""
      const numeralsRaw = JSON.parse((await readMatterFile(cwd, "numerals")) ?? '{"figures":[]}')
      const numerals = NumeralsFile.parse(numeralsRaw)
      const drifts = findNumeralDrift(spec, numerals)
      const content = JSON.stringify(drifts, null, 2)
      return { output: drifts, content }
    },
  })
}

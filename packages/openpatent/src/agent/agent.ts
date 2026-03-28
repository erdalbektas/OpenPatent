import { Config } from "../config/config"
import z from "zod"
import { Provider } from "../provider/provider"
import { generateObject, streamObject, type ModelMessage } from "ai"
import { SystemPrompt } from "../session/system"
import { Instance } from "../project/instance"
import { Truncate } from "../tool/truncation"
import { Auth } from "../auth"
import { ProviderTransform } from "../provider/transform"

import PROMPT_GENERATE from "./generate.txt"
import PROMPT_COMPACTION from "./prompt/compaction.txt"
import PROMPT_PRIOR_ART from "./prompt/prior-art.txt"
import PROMPT_CLAIMS_ANALYST from "./prompt/claims-analyst.txt"
import PROMPT_LEGAL_RESEARCH from "./prompt/legal-research.txt"
import PROMPT_DOCUMENT_WRITER from "./prompt/document-writer.txt"
import PROMPT_DRAWINGS from "./prompt/drawings.txt"
import PROMPT_REVIEWER from "./prompt/reviewer.txt"
import PROMPT_SUMMARY from "./prompt/summary.txt"
import PROMPT_TITLE from "./prompt/title.txt"
import { PermissionNext } from "@/permission/next"
import { mergeDeep, pipe, sortBy, values } from "remeda"
import { Global } from "@/global"
import path from "path"
import { Plugin } from "@/plugin"
import { Skill } from "../skill"
import { OpenPatentAuth } from "../auth/openpatent"

export const PAID_AGENTS = new Set([
  "litigate",
  "manage",
  "strategy",
  "claims-analyst",
  "legal-research",
  "document-writer",
  "reviewer",
])

export const PlanTier = z.enum(["free", "pro", "enterprise"])
export type PlanTier = z.infer<typeof PlanTier>

export class AgentPlanError extends Error {
  constructor(
    public agentName: string,
    public requiredPlan: "pro" | "enterprise",
  ) {
    super(`Agent "${agentName}" requires a ${requiredPlan} plan. Please upgrade at https://openpatent.techtank.com.tr`)
    this.name = "AgentPlanError"
  }
}

function isPaidAgent(name: string): boolean {
  return PAID_AGENTS.has(name)
}

let cachedPlan: { plan: PlanTier; expires: number } | null = null
const PLAN_CACHE_TTL = 60 * 1000 // 1 minute

export async function getUserPlan(): Promise<PlanTier> {
  // Check cache first
  if (cachedPlan && cachedPlan.expires > Date.now()) {
    return cachedPlan.plan
  }

  const auth = await OpenPatentAuth.get()
  if (!auth) {
    cachedPlan = { plan: "free", expires: Date.now() + PLAN_CACHE_TTL }
    return "free"
  }

  const isValid = await OpenPatentAuth.isValid()
  if (!isValid) {
    cachedPlan = { plan: "free", expires: Date.now() + PLAN_CACHE_TTL }
    return "free"
  }

  const plan = auth.plan ?? "free"
  cachedPlan = { plan, expires: Date.now() + PLAN_CACHE_TTL }
  return plan
}

export function invalidatePlanCache() {
  cachedPlan = null
}

export async function canUseAgent(
  agentName: string,
  verifyWithServer: boolean = false,
): Promise<{ allowed: true } | { allowed: false; requiredPlan: "pro" | "enterprise"; error: string }> {
  if (!isPaidAgent(agentName)) {
    return { allowed: true }
  }

  // For sensitive operations, verify with server
  if (verifyWithServer) {
    const isValidServer = await OpenPatentAuth.isValidServer()
    if (!isValidServer) {
      return {
        allowed: false,
        requiredPlan: "pro",
        error: `Your session has expired. Please run 'openpatent auth openpatent login' to re-authenticate.`,
      }
    }
  }

  const userPlan = await getUserPlan()

  if (userPlan === "enterprise") {
    return { allowed: true }
  }

  if (userPlan === "pro") {
    if (agentName === "litigate" || agentName === "strategy") {
      return { allowed: false, requiredPlan: "enterprise", error: "Agent requires enterprise plan" }
    }
    return { allowed: true }
  }

  return {
    allowed: false,
    requiredPlan: "pro",
    error: `Agent "${agentName}" requires a pro plan. Please upgrade at https://openpatent.techtank.com.tr`,
  }
}

export namespace Agent {
  export const Info = z
    .object({
      name: z.string(),
      description: z.string().optional(),
      mode: z.enum(["subagent", "primary", "all"]),
      native: z.boolean().optional(),
      hidden: z.boolean().optional(),
      topP: z.number().optional(),
      temperature: z.number().optional(),
      color: z.string().optional(),
      permission: PermissionNext.Ruleset,
      model: z
        .object({
          modelID: z.string(),
          providerID: z.string(),
        })
        .optional(),
      variant: z.string().optional(),
      prompt: z.string().optional(),
      options: z.record(z.string(), z.any()),
      steps: z.number().int().positive().optional(),
    })
    .meta({
      ref: "Agent",
    })
  export type Info = z.infer<typeof Info>

  const state = Instance.state(async () => {
    const cfg = await Config.get()

    const skillDirs = await Skill.dirs()
    const whitelistedDirs = [Truncate.GLOB, ...skillDirs.map((dir) => path.join(dir, "*"))]
    const defaults = PermissionNext.fromConfig({
      "*": "allow",
      doom_loop: "ask",
      external_directory: {
        "*": "ask",
        ...Object.fromEntries(whitelistedDirs.map((dir) => [dir, "allow"])),
      },
      question: "deny",
      plan_enter: "deny",
      plan_exit: "deny",
      // mirrors github.com/github/gitignore Node.gitignore pattern for .env files
      read: {
        "*": "allow",
        "*.env": "ask",
        "*.env.*": "ask",
        "*.env.example": "allow",
      },
    })
    const user = PermissionNext.fromConfig(cfg.permission ?? {})

    const result: Record<string, Info> = {
      // ── Primary Agents (user-facing workflow modes) ──
      draft: {
        name: "draft",
        description:
          "The default agent. Drafts patent applications — claims, specification, abstract, drawings descriptions.",
        options: {},
        permission: PermissionNext.merge(
          defaults,
          PermissionNext.fromConfig({
            question: "allow",
            plan_enter: "allow",
          }),
          user,
        ),
        mode: "primary",
        native: true,
      },
      prosecute: {
        name: "prosecute",
        description:
          "Responds to office actions — analyzes rejections, drafts amendments, constructs arguments, handles RCEs and appeals.",
        options: {},
        permission: PermissionNext.merge(
          defaults,
          PermissionNext.fromConfig({
            question: "allow",
          }),
          user,
        ),
        mode: "primary",
        native: true,
      },
      consult: {
        name: "consult",
        description:
          "Read-only consulting — patentability opinions, FTO analysis, landscape analysis, validity opinions. Cannot edit patent documents.",
        options: {},
        permission: PermissionNext.merge(
          defaults,
          PermissionNext.fromConfig({
            question: "allow",
            edit: "deny",
            write: "deny",
          }),
          user,
        ),
        mode: "primary",
        native: true,
      },
      litigate: {
        name: "litigate",
        description:
          "Litigation support — claim construction, infringement analysis, invalidity contentions, damages analysis.",
        options: {},
        permission: PermissionNext.merge(
          defaults,
          PermissionNext.fromConfig({
            question: "allow",
          }),
          user,
        ),
        mode: "primary",
        native: true,
      },
      manage: {
        name: "manage",
        description:
          "Portfolio management — docket tracking, deadline monitoring, status reports, maintenance fee decisions.",
        options: {},
        permission: PermissionNext.merge(
          defaults,
          PermissionNext.fromConfig({
            question: "allow",
            edit: "deny",
          }),
          user,
        ),
        mode: "primary",
        native: true,
      },
      strategy: {
        name: "strategy",
        description:
          "Planning mode. Analyzes prior art landscape, outlines claim strategy. Disallows all edit tools except plans.",
        options: {},
        permission: PermissionNext.merge(
          defaults,
          PermissionNext.fromConfig({
            question: "allow",
            plan_exit: "allow",
            external_directory: {
              [path.join(Global.Path.data, "plans", "*")]: "allow",
            },
            edit: {
              "*": "deny",
              [path.join(".openpatent", "plans", "*.md")]: "allow",
              [path.relative(Instance.worktree, path.join(Global.Path.data, path.join("plans", "*.md")))]: "allow",
            },
          }),
          user,
        ),
        mode: "primary",
        native: true,
      },
      draw: {
        name: "draw",
        description:
          "Creates patent drawings — flowcharts, system diagrams, process flows. Generates USPTO-compliant SVG drawings with reference numerals and figure numbers.",
        options: {},
        permission: PermissionNext.merge(
          defaults,
          PermissionNext.fromConfig({
            question: "allow",
          }),
          user,
        ),
        mode: "primary",
        native: true,
      },

      // ── Subagents (specialist functions) ──
      "prior-art": {
        name: "prior-art",
        permission: PermissionNext.merge(
          defaults,
          PermissionNext.fromConfig({
            "*": "deny",
            grep: "allow",
            glob: "allow",
            list: "allow",
            bash: "allow",
            webfetch: "allow",
            websearch: "allow",
            "patent-search": "allow",
            read: "allow",
            external_directory: {
              "*": "ask",
              ...Object.fromEntries(whitelistedDirs.map((dir) => [dir, "allow"])),
            },
          }),
          user,
        ),
        description: `Prior art research specialist. Use this when you need to search patent databases, find relevant references, or analyze prior art relevance. Specify thoroughness: "quick" for keyword searches, "medium" for classification-based, or "very thorough" for comprehensive multi-database analysis.`,
        prompt: PROMPT_PRIOR_ART,
        options: {},
        mode: "subagent",
        native: true,
      },
      analyst: {
        name: "analyst",
        description: `General-purpose agent for researching complex patent questions and executing multi-step analysis tasks. Use this agent to execute multiple units of work in parallel.`,
        permission: PermissionNext.merge(
          defaults,
          PermissionNext.fromConfig({
            todoread: "deny",
            todowrite: "deny",
          }),
          user,
        ),
        options: {},
        mode: "subagent",
        native: true,
      },
      "claims-analyst": {
        name: "claims-analyst",
        description: `Claims analysis specialist. Use this to parse claim structure, map elements to prior art, evaluate claim scope, and identify drafting issues.`,
        permission: PermissionNext.merge(
          defaults,
          PermissionNext.fromConfig({
            "*": "deny",
            grep: "allow",
            glob: "allow",
            list: "allow",
            read: "allow",
            bash: "allow",
            "claim-parser": "allow",
            external_directory: {
              "*": "ask",
              ...Object.fromEntries(whitelistedDirs.map((dir) => [dir, "allow"])),
            },
          }),
          user,
        ),
        prompt: PROMPT_CLAIMS_ANALYST,
        options: {},
        mode: "subagent",
        native: true,
      },
      "legal-research": {
        name: "legal-research",
        description: `Legal research specialist. Use this to search MPEP sections, find case law, analyze patent statutes, and research patent office procedures.`,
        permission: PermissionNext.merge(
          defaults,
          PermissionNext.fromConfig({
            "*": "deny",
            grep: "allow",
            glob: "allow",
            list: "allow",
            read: "allow",
            bash: "allow",
            webfetch: "allow",
            websearch: "allow",
            "mpep-lookup": "allow",
            external_directory: {
              "*": "ask",
              ...Object.fromEntries(whitelistedDirs.map((dir) => [dir, "allow"])),
            },
          }),
          user,
        ),
        prompt: PROMPT_LEGAL_RESEARCH,
        options: {},
        mode: "subagent",
        native: true,
      },
      "document-writer": {
        name: "document-writer",
        description: `Patent document drafting specialist. Use this to generate formal patent documents following PTO formatting rules and templates.`,
        permission: PermissionNext.merge(
          defaults,
          PermissionNext.fromConfig({
            todoread: "deny",
            todowrite: "deny",
          }),
          user,
        ),
        prompt: PROMPT_DOCUMENT_WRITER,
        options: {},
        mode: "subagent",
        native: true,
      },
      reviewer: {
        name: "reviewer",
        description: `Patent document review specialist. Use this to review patent documents for compliance with 35 USC §101/102/103/112, check claim drafting quality, and verify formal requirements.`,
        permission: PermissionNext.merge(
          defaults,
          PermissionNext.fromConfig({
            "*": "deny",
            grep: "allow",
            glob: "allow",
            list: "allow",
            read: "allow",
            bash: "allow",
            write: "allow",
            "claim-parser": "allow",
            "compliance-check": "allow",
            external_directory: {
              "*": "ask",
              ...Object.fromEntries(whitelistedDirs.map((dir) => [dir, "allow"])),
            },
          }),
          user,
        ),
        prompt: PROMPT_REVIEWER,
        options: {},
        mode: "subagent",
        native: true,
      },
      drawings: {
        name: "drawings",
        description: `Patent drawings specialist. Generates USPTO-compliant SVG drawings (flowcharts, block diagrams, system diagrams, process flows) and Brief Description of Drawings text for the specification.`,
        permission: PermissionNext.merge(
          defaults,
          PermissionNext.fromConfig({
            "*": "deny",
            read: "allow",
            write: "allow",
            glob: "allow",
            grep: "allow",
            list: "allow",
            external_directory: {
              "*": "ask",
              ...Object.fromEntries(whitelistedDirs.map((dir) => [dir, "allow"])),
            },
          }),
          user,
        ),
        prompt: PROMPT_DRAWINGS,
        options: {},
        mode: "subagent",
        native: true,
      },

      // ── Internal Agents (hidden) ──
      compaction: {
        name: "compaction",
        mode: "primary",
        native: true,
        hidden: true,
        prompt: PROMPT_COMPACTION,
        permission: PermissionNext.merge(
          defaults,
          PermissionNext.fromConfig({
            "*": "deny",
          }),
          user,
        ),
        options: {},
      },
      title: {
        name: "title",
        mode: "primary",
        options: {},
        native: true,
        hidden: true,
        temperature: 0.5,
        permission: PermissionNext.merge(
          defaults,
          PermissionNext.fromConfig({
            "*": "deny",
          }),
          user,
        ),
        prompt: PROMPT_TITLE,
      },
      summary: {
        name: "summary",
        mode: "primary",
        options: {},
        native: true,
        hidden: true,
        permission: PermissionNext.merge(
          defaults,
          PermissionNext.fromConfig({
            "*": "deny",
          }),
          user,
        ),
        prompt: PROMPT_SUMMARY,
      },
    }

    for (const [key, value] of Object.entries(cfg.agent ?? {})) {
      if (value.disable) {
        delete result[key]
        continue
      }
      let item = result[key]
      if (!item)
        item = result[key] = {
          name: key,
          mode: "all",
          permission: PermissionNext.merge(defaults, user),
          options: {},
          native: false,
        }
      if (value.model) item.model = Provider.parseModel(value.model)
      item.variant = value.variant ?? item.variant
      item.prompt = value.prompt ?? item.prompt
      item.description = value.description ?? item.description
      item.temperature = value.temperature ?? item.temperature
      item.topP = value.top_p ?? item.topP
      item.mode = value.mode ?? item.mode
      item.color = value.color ?? item.color
      item.hidden = value.hidden ?? item.hidden
      item.name = value.name ?? item.name
      item.steps = value.steps ?? item.steps
      item.options = mergeDeep(item.options, value.options ?? {})
      item.permission = PermissionNext.merge(item.permission, PermissionNext.fromConfig(value.permission ?? {}))
    }

    // Ensure Truncate.GLOB is allowed unless explicitly configured
    for (const name in result) {
      const agent = result[name]
      const explicit = agent.permission.some((r) => {
        if (r.permission !== "external_directory") return false
        if (r.action !== "deny") return false
        return r.pattern === Truncate.GLOB
      })
      if (explicit) continue

      result[name].permission = PermissionNext.merge(
        result[name].permission,
        PermissionNext.fromConfig({ external_directory: { [Truncate.GLOB]: "allow" } }),
      )
    }

    return result
  })

  export async function get(agent: string) {
    const result = await state().then((x) => x[agent])
    if (!result) return undefined

    // Verify with server for security - prevents fake tokens
    const check = await canUseAgent(agent, true)
    if (!check.allowed) {
      throw new AgentPlanError(agent, check.requiredPlan)
    }

    return result
  }

  export async function list() {
    const cfg = await Config.get()
    return pipe(
      await state(),
      values(),
      sortBy([(x) => (cfg.default_agent ? x.name === cfg.default_agent : x.name === "draft"), "desc"]),
    )
  }

  export async function defaultAgent() {
    const cfg = await Config.get()
    const agents = await state()

    if (cfg.default_agent) {
      const agent = agents[cfg.default_agent]
      if (!agent) throw new Error(`default agent "${cfg.default_agent}" not found`)
      if (agent.mode === "subagent") throw new Error(`default agent "${cfg.default_agent}" is a subagent`)
      if (agent.hidden === true) throw new Error(`default agent "${cfg.default_agent}" is hidden`)
      return agent.name
    }

    const primaryVisible = Object.values(agents).find((a) => a.mode !== "subagent" && a.hidden !== true)
    if (!primaryVisible) throw new Error("no primary visible agent found")
    return primaryVisible.name
  }

  export async function generate(input: { description: string; model?: { providerID: string; modelID: string } }) {
    const cfg = await Config.get()
    const defaultModel = input.model ?? (await Provider.defaultModel())
    const model = await Provider.getModel(defaultModel.providerID, defaultModel.modelID)
    const language = await Provider.getLanguage(model)

    const system = [PROMPT_GENERATE]
    await Plugin.trigger("experimental.chat.system.transform", { model }, { system })
    const existing = await list()

    const params = {
      experimental_telemetry: {
        isEnabled: cfg.experimental?.openTelemetry,
        metadata: {
          userId: cfg.username ?? "unknown",
        },
      },
      temperature: 0.3,
      messages: [
        ...system.map(
          (item): ModelMessage => ({
            role: "system",
            content: item,
          }),
        ),
        {
          role: "user",
          content: `Create an agent configuration based on this request: \"${input.description}\".\n\nIMPORTANT: The following identifiers already exist and must NOT be used: ${existing.map((i) => i.name).join(", ")}\n  Return ONLY the JSON object, no other text, do not wrap in backticks`,
        },
      ],
      model: language,
      schema: z.object({
        identifier: z.string(),
        whenToUse: z.string(),
        systemPrompt: z.string(),
      }),
    } satisfies Parameters<typeof generateObject>[0]

    if (defaultModel.providerID === "openai" && (await Auth.get(defaultModel.providerID))?.type === "oauth") {
      const result = streamObject({
        ...params,
        providerOptions: ProviderTransform.providerOptions(model, {
          instructions: SystemPrompt.instructions(),
          store: false,
        }),
        onError: () => {},
      })
      for await (const part of result.fullStream) {
        if (part.type === "error") throw part.error
      }
      return result.object
    }

    const result = await generateObject(params)
    return result.object
  }
}

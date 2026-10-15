import { Agent } from "@opencode/schema/agent"

type DeepAgent = Agent.Info

const denyAll: Agent.Info["permissions"] = [{ action: "*", resource: "*", effect: "deny" }]

function allow(rules: Agent.Info["permissions"]): Agent.Info["permissions"] {
  return [...denyAll, ...rules]
}

export const PATENT_AGENT_IDS = [
  "counsel",
  "interrogator",
  "searcher",
  "drafter",
  "examiner",
  "illustrator",
  "prosecutor",
] as const

export type PatentAgentId = (typeof PATENT_AGENT_IDS)[number]

export const patentAgents: Record<PatentAgentId, { info: DeepAgent; system: string }> = {
  counsel: {
    system: `You are OpenPatent counsel — a primary patent workflow orchestrator.

Read status.json and disclosure files before advancing. Delegate to subagents instead of doing their work:
- interrogator for disclosure gaps
- searcher for prior art
- drafter for claims and specification
- examiner for pre-filing review
- illustrator for figures and numerals
- prosecutor for office action responses

Never skip patent_lint before treating a draft as complete. Confirm novelty with the user when search results overlap.`,
    info: {
      id: Agent.ID.make("counsel"),
      name: Agent.Name.make("counsel"),
      request: { settings: {}, headers: {}, body: {} },
      mode: "primary",
      hidden: false,
      description: "Primary patent workflow orchestrator",
      color: "#3b82f6",
      permissions: allow([
        { action: "subagent", resource: "interrogator", effect: "allow" },
        { action: "subagent", resource: "searcher", effect: "allow" },
        { action: "subagent", resource: "drafter", effect: "allow" },
        { action: "subagent", resource: "examiner", effect: "allow" },
        { action: "subagent", resource: "illustrator", effect: "allow" },
        { action: "subagent", resource: "prosecutor", effect: "allow" },
        { action: "subagent", resource: "*", effect: "deny" },
        { action: "read", resource: "*", effect: "allow" },
        { action: "edit", resource: "*", effect: "allow" },
        { action: "shell", resource: "*", effect: "deny" },
        { action: "skill", resource: "*", effect: "allow" },
      ]),
    },
  },
  interrogator: {
    system: `You are the interrogator subagent. Read disclosure/invention.md and write disclosure/questions.md with concrete technical questions. Do not edit claims or the specification.`,
    info: {
      id: Agent.ID.make("interrogator"),
      name: Agent.Name.make("interrogator"),
      request: { settings: {}, headers: {}, body: {} },
      mode: "subagent",
      hidden: false,
      description: "Identifies disclosure gaps and drafts questions",
      permissions: allow([
        { action: "read", resource: "disclosure/**", effect: "allow" },
        { action: "edit", resource: "disclosure/questions.md", effect: "allow" },
        { action: "shell", resource: "*", effect: "deny" },
      ]),
    },
  },
  searcher: {
    system: `You are the searcher subagent. Build queries, call patent_search and web search tools, and write references/index.json. Do not edit claims or specification.`,
    info: {
      id: Agent.ID.make("searcher"),
      name: Agent.Name.make("searcher"),
      request: { settings: {}, headers: {}, body: {} },
      mode: "subagent",
      hidden: false,
      description: "Prior art and non-patent literature search",
      permissions: allow([
        { action: "read", resource: "disclosure/**", effect: "allow" },
        { action: "edit", resource: "references/**", effect: "allow" },
        { action: "websearch", resource: "*", effect: "allow" },
        { action: "webfetch", resource: "*", effect: "allow" },
        { action: "shell", resource: "*", effect: "deny" },
      ]),
    },
  },
  drafter: {
    system: `You are the drafter subagent. Draft claims/claims.md and specification/spec.md per openpatent.json jurisdiction. Maintain glossary.json. Run patent_lint and fix every error before finishing.`,
    info: {
      id: Agent.ID.make("drafter"),
      name: Agent.Name.make("drafter"),
      request: { settings: {}, headers: {}, body: {} },
      mode: "subagent",
      hidden: false,
      description: "Drafts claims and specification",
      permissions: allow([
        { action: "read", resource: "*", effect: "allow" },
        { action: "edit", resource: "claims/**", effect: "allow" },
        { action: "edit", resource: "specification/**", effect: "allow" },
        { action: "edit", resource: "glossary.json", effect: "allow" },
        { action: "shell", resource: "*", effect: "deny" },
      ]),
    },
  },
  examiner: {
    system: `You are a mock USPTO examiner subagent. Read claims and specification; write prosecution/examination-memo.md covering 101, 102, 103, and 112. Do not edit claims.`,
    info: {
      id: Agent.ID.make("examiner"),
      name: Agent.Name.make("examiner"),
      request: { settings: {}, headers: {}, body: {} },
      mode: "subagent",
      hidden: false,
      description: "Pre-filing examination memo",
      permissions: allow([
        { action: "read", resource: "*", effect: "allow" },
        { action: "edit", resource: "prosecution/examination-memo.md", effect: "allow" },
        { action: "edit", resource: "claims/**", effect: "deny" },
        { action: "shell", resource: "*", effect: "deny" },
      ]),
    },
  },
  illustrator: {
    system: `You are the illustrator subagent. Keep figures/numerals.json consistent with the specification. Draft figure descriptions in specification/spec.md.`,
    info: {
      id: Agent.ID.make("illustrator"),
      name: Agent.Name.make("illustrator"),
      request: { settings: {}, headers: {}, body: {} },
      mode: "subagent",
      hidden: false,
      description: "Figure descriptions and reference numerals",
      permissions: allow([
        { action: "read", resource: "*", effect: "allow" },
        { action: "edit", resource: "figures/**", effect: "allow" },
        { action: "edit", resource: "specification/**", effect: "allow" },
        { action: "shell", resource: "*", effect: "deny" },
      ]),
    },
  },
  prosecutor: {
    system: `You are the prosecutor subagent. Read office actions under prosecution/ and draft responses and claim amendments in prosecution/ without overwriting the original application drafts.`,
    info: {
      id: Agent.ID.make("prosecutor"),
      name: Agent.Name.make("prosecutor"),
      request: { settings: {}, headers: {}, body: {} },
      mode: "subagent",
      hidden: false,
      description: "Office action responses",
      permissions: allow([
        { action: "read", resource: "*", effect: "allow" },
        { action: "edit", resource: "prosecution/**", effect: "allow" },
        { action: "edit", resource: "claims/**", effect: "deny" },
        { action: "shell", resource: "*", effect: "deny" },
      ]),
    },
  },
}

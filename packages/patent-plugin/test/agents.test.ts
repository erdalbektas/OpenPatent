import { describe, expect, test } from "bun:test"
import { patentAgents, PATENT_AGENT_IDS } from "../src/agents"

describe("patent agents", () => {
  test("registers seven agents with counsel as primary orchestrator", () => {
    expect(PATENT_AGENT_IDS).toHaveLength(7)
    expect(patentAgents.counsel.info.mode).toBe("primary")
    const subagents = PATENT_AGENT_IDS.filter((id) => id !== "counsel")
    for (const id of subagents) {
      expect(patentAgents[id].info.mode).toBe("subagent")
    }
  })

  test("counsel may only launch patent subagents", () => {
    const rules = patentAgents.counsel.info.permissions
    const subagentRules = rules.filter((r) => r.action === "subagent")
    expect(subagentRules.some((r) => r.resource === "drafter" && r.effect === "allow")).toBe(true)
    expect(subagentRules.some((r) => r.resource === "*" && r.effect === "deny")).toBe(true)
  })

  test("drafter cannot use shell", () => {
    const rules = patentAgents.drafter.info.permissions
    expect(rules.some((r) => r.action === "shell" && r.effect === "deny")).toBe(true)
  })

  test("examiner cannot edit claims", () => {
    const rules = patentAgents.examiner.info.permissions
    expect(rules.some((r) => r.action === "edit" && r.resource === "claims/**" && r.effect === "deny")).toBe(true)
  })
})

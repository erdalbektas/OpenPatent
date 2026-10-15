import { parseClaims, claimDependencyChain, type ParsedClaim } from "./claims"
import type { Jurisdiction } from "./matter"

export type LintSeverity = "error" | "warning"

export type LintIssue = {
  severity: LintSeverity
  code: string
  message: string
  claim?: number
  line?: number
}

export type LintResult = {
  clean: boolean
  issues: LintIssue[]
}

export type BannedWordMap = Record<string, string>

const DEFAULT_BANNED: BannedWordMap = {
  approximately: "Replace with a specific tolerance or range.",
  substantially: "Define technical parameters instead.",
  about: "Use a definite numerical bound.",
  "similar to": "Describe shared structural features.",
  "user-friendly": "Use measurable interface criteria.",
}

export function lintClaims(
  claimsText: string,
  options: { jurisdiction?: Jurisdiction; bannedWords?: BannedWordMap } = {},
): LintResult {
  const { claims } = parseClaims(claimsText)
  const issues: LintIssue[] = []
  const banned = { ...DEFAULT_BANNED, ...options.bannedWords }
  const jurisdiction = options.jurisdiction ?? "USPTO"

  for (const claim of claims) {
    issues.push(...lintAntecedentBasis(claims, claim))
    issues.push(...lintBannedWords(claim, banned))
    issues.push(...lintJurisdiction(claim, jurisdiction))
  }

  const errors = issues.filter((i) => i.severity === "error")
  return { clean: errors.length === 0, issues }
}

function lintAntecedentBasis(all: ParsedClaim[], claim: ParsedClaim): LintIssue[] {
  const issues: LintIssue[] = []
  const chain = claimDependencyChain(all, claim.number)
  const introduced = new Set<string>()

  for (const num of chain) {
    const c = all.find((x) => x.number === num)
    if (!c) continue
    const text = c.body
    for (const m of text.matchAll(/\b(?:a|an)\s+([a-zA-Z][\w-]*)/gi)) {
      const term = m[1]
      if (term) introduced.add(term.toLowerCase())
    }
    const refs = [...text.matchAll(/\b(?:the|said)\s+([a-zA-Z][\w-]*)/gi)]
    for (const m of refs) {
      const term = m[1]?.toLowerCase()
      if (!term) continue
      if (term === "claim") continue
      if (!introduced.has(term)) {
        issues.push({
          severity: "error",
          code: "antecedent_basis",
          message: `Claim ${c.number} references "the ${m[1] ?? "?"}" without prior introduction in the claim chain.`,
          claim: c.number,
        })
      }
    }
  }

  return issues
}

function lintBannedWords(claim: ParsedClaim, banned: BannedWordMap): LintIssue[] {
  const issues: LintIssue[] = []
  const lines = claim.raw.split(/\r?\n/)
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i] ?? ""
    for (const [word, suggestion] of Object.entries(banned)) {
      const re = new RegExp(`\\b${escapeRegExp(word)}\\b`, "i")
      if (re.test(line)) {
        issues.push({
          severity: "error",
          code: "indefiniteness",
          message: `Banned term "${word}". ${suggestion}`,
          claim: claim.number,
          line: i + 1,
        })
      }
    }
  }
  return issues
}

function lintJurisdiction(claim: ParsedClaim, jurisdiction: Jurisdiction): LintIssue[] {
  if (jurisdiction !== "EPO") return []
  if (!/characterized in that/i.test(claim.body) && claim.dependsOn.length === 0) {
    return [
      {
        severity: "warning",
        code: "epo_two_part",
        message: `Claim ${claim.number}: independent EPO claims should use two-part form ("characterized in that").`,
        claim: claim.number,
      },
    ]
  }
  return []
}

function escapeRegExp(s: string) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
}

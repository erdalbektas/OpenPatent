import { z } from "zod"

export const ClaimType = z.enum(["method", "system", "composition", "other"])
export type ClaimType = z.infer<typeof ClaimType>

export const ParsedClaim = z.object({
  number: z.number().int().positive(),
  dependsOn: z.array(z.number().int().positive()),
  type: ClaimType,
  transition: z.string().optional(),
  preamble: z.string(),
  body: z.string(),
  elements: z.array(z.string()),
  raw: z.string(),
})
export type ParsedClaim = z.infer<typeof ParsedClaim>

export const ParsedClaimSet = z.object({
  claims: z.array(ParsedClaim),
})
export type ParsedClaimSet = z.infer<typeof ParsedClaimSet>

const CLAIM_START = /^\s*(\d+)\.\s+/

export function parseClaims(text: string): ParsedClaimSet {
  const blocks = splitClaimBlocks(text)
  const claims: ParsedClaim[] = []

  for (const block of blocks) {
    const match = block.match(CLAIM_START)
    if (!match) continue
    const number = Number.parseInt(match[1]!, 10)
    const bodyText = block.slice(match[0].length).trim()
    const dependsOn = parseDependencies(bodyText)
    const transition = parseTransition(bodyText)
    const type = inferClaimType(bodyText)
    const elements = splitElements(bodyText)
    const preamble = elements[0] ?? bodyText

    claims.push({
      number,
      dependsOn,
      type,
      transition,
      preamble,
      body: bodyText,
      elements,
      raw: block.trim(),
    })
  }

  return { claims }
}

function splitClaimBlocks(text: string): string[] {
  const lines = text.split(/\r?\n/)
  const blocks: string[] = []
  let current: string[] = []

  for (const line of lines) {
    if (CLAIM_START.test(line) && current.length > 0) {
      blocks.push(current.join("\n"))
      current = [line]
    } else {
      current.push(line)
    }
  }
  if (current.length > 0) blocks.push(current.join("\n"))
  return blocks.filter((b) => b.trim().length > 0)
}

function parseDependencies(text: string): number[] {
  const deps = new Set<number>()
  const patterns = [
    /\bclaim\s+(\d+)\b/gi,
    /\bclaims?\s+(\d+)\s+and\s+(\d+)/gi,
    /\bclaims?\s+(\d+)\s*(?:,|or)\s*(\d+)/gi,
  ]
  for (const re of patterns) {
    let m: RegExpExecArray | null
    while ((m = re.exec(text)) !== null) {
      for (let i = 1; i < m.length; i++) {
        const n = m[i]
        if (n) deps.add(Number.parseInt(n, 10))
      }
    }
  }
  return [...deps].sort((a, b) => a - b)
}

function parseTransition(text: string): string | undefined {
  const m = text.match(/\b(comprising|consisting essentially of|consisting of|including|characterized in that)\b/i)
  return m?.[1]
}

function inferClaimType(text: string): ClaimType {
  const lower = text.toLowerCase()
  if (/\b(a|an)\s+method\b/.test(lower)) return "method"
  if (/\b(a|an)\s+system\b/.test(lower) || /\bapparatus\b/.test(lower)) return "system"
  if (/\bcomposition\b/.test(lower)) return "composition"
  return "other"
}

function splitElements(text: string): string[] {
  const normalized = text.replace(/\s+/g, " ").trim()
  const afterTransition = normalized.split(/\b(?:comprising|consisting essentially of|consisting of|including)\b/i)[1]
  const segment = (afterTransition ?? normalized).trim()
  if (!segment) return [normalized]

  const parts = segment
    .split(/;\s*|,\s+(?=(?:wherein|further|and)\b)/i)
    .map((p) => p.trim())
    .filter(Boolean)

  return parts.length > 0 ? parts : [segment]
}

export function claimDependencyChain(claims: ParsedClaim[], number: number): number[] {
  const byNum = new Map(claims.map((c) => [c.number, c]))
  const chain: number[] = []
  const seen = new Set<number>()
  let current = byNum.get(number)
  while (current) {
    if (seen.has(current.number)) break
    seen.add(current.number)
    chain.push(current.number)
    const parent = current.dependsOn[current.dependsOn.length - 1]
    current = parent ? byNum.get(parent) : undefined
  }
  return chain.reverse()
}

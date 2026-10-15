import { z } from "zod"
import { parseClaims, type ParsedClaim } from "./claims"

export const ChartMethod = z.enum(["word_overlap"])
export type ChartMethod = z.infer<typeof ChartMethod>

export const ChartMapping = z.object({
  element: z.string(),
  referenceId: z.string(),
  referenceExcerpt: z.string().optional(),
  similarity: z.number(),
  method: ChartMethod,
})
export type ChartMapping = z.infer<typeof ChartMapping>

export const ClaimChart = z.object({
  claimNumber: z.number(),
  referenceId: z.string(),
  method: ChartMethod,
  mappings: z.array(ChartMapping),
})
export type ClaimChart = z.infer<typeof ClaimChart>

export function wordOverlapSimilarity(a: string, b: string): number {
  const wordsA = new Set(a.toLowerCase().match(/\b\w+\b/g) ?? [])
  const wordsB = new Set(b.toLowerCase().match(/\b\w+\b/g) ?? [])
  if (wordsA.size === 0 || wordsB.size === 0) return 0
  let inter = 0
  for (const w of wordsA) if (wordsB.has(w)) inter++
  return inter / Math.max(wordsA.size, wordsB.size)
}

export function buildClaimChart(
  claim: ParsedClaim,
  referenceId: string,
  referenceText: string,
  threshold = 0.35,
): ClaimChart {
  const refElements = referenceText.split(/[.;]\s+/).filter(Boolean)
  const mappings: ChartMapping[] = []

  for (const element of claim.elements) {
    let best = { score: 0, excerpt: "" }
    for (const refEl of refElements) {
      const score = wordOverlapSimilarity(element, refEl)
      if (score > best.score) best = { score, excerpt: refEl }
    }
    if (best.score >= threshold) {
      mappings.push({
        element,
        referenceId,
        referenceExcerpt: best.excerpt,
        similarity: best.score,
        method: "word_overlap",
      })
    }
  }

  return {
    claimNumber: claim.number,
    referenceId,
    method: "word_overlap",
    mappings,
  }
}

export function chartFromClaimSet(claimsText: string, referenceId: string, referenceText: string): ClaimChart[] {
  const { claims } = parseClaims(claimsText)
  return claims.map((c) => buildClaimChart(c, referenceId, referenceText))
}

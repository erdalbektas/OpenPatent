import { z } from "zod"

export const NumeralsFile = z.object({
  figures: z.array(
    z.object({
      id: z.string(),
      description: z.string().optional(),
      numerals: z.record(z.string(), z.string()),
    }),
  ),
})
export type NumeralsFile = z.infer<typeof NumeralsFile>

export type NumeralDrift = {
  numeral: string
  labelInSpec?: string
  labelInFigures?: string
  message: string
}

export function findNumeralDrift(specText: string, numerals: NumeralsFile): NumeralDrift[] {
  const drifts: NumeralDrift[] = []
  const figureLabels = new Map<string, string>()

  for (const fig of numerals.figures) {
    for (const [num, label] of Object.entries(fig.numerals)) {
      figureLabels.set(num, label)
    }
  }

  for (const [num, figLabel] of figureLabels) {
    const re = new RegExp(`\\b${escapeRegExp(figLabel)}\\s+${escapeRegExp(num)}\\b`, "i")
    const alt = new RegExp(`\\b${escapeRegExp(num)}\\b[^\\n]{0,40}\\b${escapeRegExp(figLabel)}\\b`, "i")
    if (!re.test(specText) && !alt.test(specText)) {
      drifts.push({
        numeral: num,
        labelInFigures: figLabel,
        message: `Reference numeral ${num} (${figLabel}) not found in specification.`,
      })
    }
  }

  const specRefs = [...specText.matchAll(/\b([A-Za-z][\w-]*)\s+(\d{2,4})\b/g)]
  for (const m of specRefs) {
    const label = m[1]
    const num = m[2]
    if (!label || !num) continue
    const expected = figureLabels.get(num)
    if (expected && expected.toLowerCase() !== label.toLowerCase()) {
      drifts.push({
        numeral: num,
        labelInSpec: label,
        labelInFigures: expected,
        message: `Numeral ${num}: specification uses "${label}" but figures define "${expected}".`,
      })
    }
  }

  return drifts
}

function escapeRegExp(s: string) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
}

import { z } from "zod"

export const Glossary = z.record(z.string(), z.string())
export type Glossary = z.infer<typeof Glossary>

export function parseGlossary(text: string): Glossary {
  const raw = JSON.parse(text)
  return Glossary.parse(raw)
}

export function mergeGlossary(current: Glossary, updates: Glossary): Glossary {
  return { ...current, ...updates }
}

export function formatGlossary(glossary: Glossary): string {
  return JSON.stringify(glossary, null, 2) + "\n"
}

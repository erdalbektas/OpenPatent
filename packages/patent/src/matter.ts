import { z } from "zod"
import path from "node:path"
import { existsSync } from "node:fs"

export const Jurisdiction = z.enum(["USPTO", "EPO", "WIPO"])
export type Jurisdiction = z.infer<typeof Jurisdiction>

export const OpenPatentConfig = z.object({
  title: z.string().min(1),
  docketId: z.string().optional(),
  jurisdiction: Jurisdiction.default("USPTO"),
})
export type OpenPatentConfig = z.infer<typeof OpenPatentConfig>

export const MATTER_PATHS = {
  config: "openpatent.json",
  invention: "disclosure/invention.md",
  questions: "disclosure/questions.md",
  claims: "claims/claims.md",
  specification: "specification/spec.md",
  numerals: "figures/numerals.json",
  references: "references/index.json",
  glossary: "glossary.json",
  prosecutionDir: "prosecution",
  status: "status.json",
} as const

export function matterRoot(cwd: string) {
  return path.resolve(cwd)
}

export function matterPath(cwd: string, key: keyof typeof MATTER_PATHS) {
  return path.join(matterRoot(cwd), MATTER_PATHS[key])
}

export function isMatterDirectory(cwd: string) {
  return existsSync(matterPath(cwd, "config"))
}

export const MatterStatusGates = z.object({
  disclosure: z.boolean(),
  questionsAnswered: z.boolean(),
  references: z.boolean(),
  claims: z.boolean(),
  specification: z.boolean(),
  lintClean: z.boolean().optional(),
  examinationMemo: z.boolean().optional(),
})
export type MatterStatusGates = z.infer<typeof MatterStatusGates>

export async function readConfig(cwd: string): Promise<OpenPatentConfig | null> {
  const file = Bun.file(matterPath(cwd, "config"))
  if (!(await file.exists())) return null
  const raw = JSON.parse(await file.text())
  return OpenPatentConfig.parse(raw)
}

export async function matterStatusFromFiles(cwd: string): Promise<MatterStatusGates> {
  const read = async (key: keyof typeof MATTER_PATHS) => {
    const file = Bun.file(matterPath(cwd, key))
    if (!(await file.exists())) return false
    const text = (await file.text()).trim()
    return text.length > 0
  }

  const questions = await read("questions")
  const questionsAnswered = questions && !(await fileLooksLikeOpenQuestions(cwd))

  return {
    disclosure: await read("invention"),
    questionsAnswered,
    references: await read("references"),
    claims: await read("claims"),
    specification: await read("specification"),
  }
}

async function fileLooksLikeOpenQuestions(cwd: string) {
  const file = Bun.file(matterPath(cwd, "questions"))
  if (!(await file.exists())) return true
  const text = await file.text()
  return /\[?\s*unanswered\s*\]?/i.test(text) || text.includes("TODO:")
}

export const DEFAULT_STATUS_JSON = {
  phase: "intake",
  updatedAt: null as string | null,
  lint: { clean: false, errorCount: 0 },
} as const

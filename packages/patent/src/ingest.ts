import path from "node:path"
import { MATTER_PATHS } from "./matter"

export type IngestResult = {
  path: string
  bytes: number
}

export async function ingestDisclosureFile(cwd: string, sourcePath: string): Promise<IngestResult> {
  const abs = path.resolve(sourcePath)
  const file = Bun.file(abs)
  if (!(await file.exists())) throw new Error(`File not found: ${abs}`)

  const ext = path.extname(abs).toLowerCase()
  let text: string

  if (ext === ".md" || ext === ".txt") {
    text = await file.text()
  } else if (ext === ".pdf" || ext === ".docx") {
    throw new Error(
      `Binary format ${ext} requires an external extractor. Convert to markdown or plain text before ingest.`,
    )
  } else {
    text = await file.text()
  }

  const dest = path.join(cwd, MATTER_PATHS.invention)
  await Bun.write(dest, text.endsWith("\n") ? text : text + "\n")
  return { path: dest, bytes: text.length }
}

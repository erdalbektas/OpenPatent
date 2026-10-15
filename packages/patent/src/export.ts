import { MATTER_PATHS, readConfig } from "./matter"
import path from "node:path"

export async function exportApplicationMarkdown(cwd: string): Promise<string> {
  const config = await readConfig(cwd)
  const title = config?.title ?? "Patent Application"

  const read = async (rel: string) => {
    const file = Bun.file(path.join(cwd, rel))
    if (!(await file.exists())) return ""
    return await file.text()
  }

  const invention = await read(MATTER_PATHS.invention)
  const claims = await read(MATTER_PATHS.claims)
  const spec = await read(MATTER_PATHS.specification)

  return `# ${title}

## Field of the Invention

${invention.split("\n").slice(0, 5).join("\n")}

## Brief Summary

${invention}

## Claims

${claims}

## Detailed Description

${spec}
`
}

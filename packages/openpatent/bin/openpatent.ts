#!/usr/bin/env bun
import path from "node:path"
import { fileURLToPath } from "node:url"
import { initMatter } from "@openpatent/patent/init"
import { spawn } from "node:child_process"

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(__dirname, "../../..")

async function main() {
  const args = process.argv.slice(2)
  const cmd = args[0]

  if (cmd === "init") {
    const target = args[1] ?? "."
    const titleFlag = args.indexOf("--title")
    const title = titleFlag >= 0 ? args[titleFlag + 1] : "Untitled invention"
    const jurisdictionFlag = args.indexOf("--jurisdiction")
    const jurisdiction = (jurisdictionFlag >= 0 ? args[jurisdictionFlag + 1] : "USPTO") as "USPTO" | "EPO" | "WIPO"
    const root = await initMatter(path.resolve(target), { title, jurisdiction })
    console.log(`OpenPatent matter initialized at ${root}`)
    return
  }

  const cliEntry = path.join(repoRoot, "packages/cli/src/index.ts")
  const child = spawn(process.execPath, ["run", cliEntry, ...args], {
    stdio: "inherit",
    cwd: process.cwd(),
    env: {
      ...process.env,
      OPENCODE_PRODUCT: "openpatent",
    },
  })
  const code = await new Promise<number>((resolve) => child.on("close", (c) => resolve(c ?? 1)))
  process.exit(code)
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})

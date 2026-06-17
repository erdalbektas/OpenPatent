import { $ } from "bun"

import { copyBinaryToSidecarFolder, getCurrentSidecar, windowsify } from "./utils"

const version = Bun.env.OPENCODE_VERSION ?? (await Bun.file(new URL("../package.json", import.meta.url)).json()).version
const baseline = process.argv.includes("--baseline")
const target = Bun.env.RUST_TARGET ?? Bun.env.TAURI_ENV_TARGET_TRIPLE

if (!target) throw new Error("Set RUST_TARGET or TAURI_ENV_TARGET_TRIPLE")

const sidecar = getCurrentSidecar(target)
const binaryPath = windowsify(`../openpatent/dist/${sidecar.ocBinary}/bin/opencode`)

await (baseline
  ? $`cd ../openpatent && OPENCODE_VERSION=${version} bun run build --single --baseline`
  : $`cd ../openpatent && OPENCODE_VERSION=${version} bun run build --single`)

await copyBinaryToSidecarFolder(binaryPath, target)

const dest = windowsify(`src-tauri/sidecars/openpatent-cli-${target}`)
const check = await $`${dest} --version`.quiet().nothrow()
if (check.exitCode !== 0) throw new Error(`Sidecar version check failed for ${dest}`)

console.log(`Sidecar ${dest} -> ${check.stdout.toString().trim()}`)

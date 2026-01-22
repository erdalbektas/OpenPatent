#!/usr/bin/env bun
import { $ } from "bun"

import { copyBinaryToSidecarFolder, getCurrentSidecar } from "./utils"

const sidecarConfig = getCurrentSidecar()

const dir = "src-tauri/target/openpatent-binaries"

await $`mkdir -p ${dir}`
await $`gh run download ${Bun.env.GITHUB_RUN_ID} -n openpatent-cli`.cwd(dir)

await copyBinaryToSidecarFolder(
  `${dir}/${sidecarConfig.ocBinary}/bin/openpatent${process.platform === "win32" ? ".exe" : ""}`,
)

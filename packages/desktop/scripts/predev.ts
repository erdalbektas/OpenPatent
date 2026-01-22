import { $ } from "bun"

import { copyBinaryToSidecarFolder, getCurrentSidecar } from "./utils"

const RUST_TARGET = Bun.env.TAURI_ENV_TARGET_TRIPLE

const sidecarConfig = getCurrentSidecar(RUST_TARGET)

const binaryPath = `../openpatent/dist/${sidecarConfig.ocBinary}/bin/openpatent`

await $`cd ../openpatent && bun run build --single`

await copyBinaryToSidecarFolder(binaryPath, RUST_TARGET)

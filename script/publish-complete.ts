#!/usr/bin/env bun

import { Script } from "@openpatent-ai/script"
import { $ } from "bun"

if (!Script.preview) {
  await $`gh release edit v${Script.version} --draft=false`
}

await $`bun install`

await $`gh release download --pattern "openpatent-linux-*64.tar.gz" --pattern "openpatent-darwin-*64.zip" -D dist`

await import(`../packages/openpatent/script/publish-registries.ts`)

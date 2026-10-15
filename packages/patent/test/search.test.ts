import { describe, expect, test } from "bun:test"
import { createPatentsViewProvider, SearchNotConfiguredError } from "../src/search"

describe("patent search", () => {
  test("throws when API key missing", async () => {
    const provider = createPatentsViewProvider(undefined)
    await expect(provider.search("widget")).rejects.toBeInstanceOf(SearchNotConfiguredError)
  })
})

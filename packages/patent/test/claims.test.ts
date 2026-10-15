import { describe, expect, test } from "bun:test"
import { parseClaims, claimDependencyChain } from "../src/claims"
import { lintClaims } from "../src/lint"

describe("parseClaims", () => {
  test("parses independent and dependent claims", () => {
    const text = `
1. A method comprising receiving data from a sensor.

2. The method of claim 1, further comprising filtering the data.
`
    const { claims } = parseClaims(text)
    expect(claims.length).toBe(2)
    expect(claims[0]?.type).toBe("method")
    expect(claims[1]?.dependsOn).toContain(1)
  })
})

describe("lintClaims", () => {
  test("flags approximately", () => {
    const text = `1. A system comprising approximately five processors.`
    const result = lintClaims(text)
    expect(result.clean).toBe(false)
    expect(result.issues.some((i) => i.code === "indefiniteness")).toBe(true)
  })

  test("flags antecedent basis through dependent chain", () => {
    const text = `
1. A method comprising receiving data.

2. The method of claim 1, further comprising transmitting the payload to the widget.
`
    const result = lintClaims(text)
    expect(result.clean).toBe(false)
    expect(result.issues.some((i) => i.code === "antecedent_basis" && i.claim === 2)).toBe(true)
  })

  test("allows introduced term in parent chain", () => {
    const text = `
1. A method comprising receiving data from a sensor.

2. The method of claim 1, further comprising filtering the sensor output.
`
    const chain = claimDependencyChain(parseClaims(text).claims, 2)
    expect(chain).toEqual([1, 2])
    const result = lintClaims(text)
    expect(result.issues.filter((i) => i.code === "antecedent_basis")).toHaveLength(0)
  })
})

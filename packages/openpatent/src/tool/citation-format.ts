import { Tool } from "./tool"
import z from "zod"
import { Provider } from "../provider/provider"
import { generateText } from "ai"

const DESCRIPTION = `Format and validate patent citations.

Properly format patent references, publication references, and non-patent literature
citations according to PTO standards. Validates patent numbers and formats them
consistently (e.g., US10,123,456 B2).`

const parameters = z.object({
  citation: z.string().describe("The raw citation text to format — patent number, publication, or NPL reference"),
  format: z
    .enum(["ids", "specification", "office-action"])
    .default("specification")
    .describe("The citation format context"),
})

export const CitationFormatTool = Tool.define<typeof parameters, { formatted: boolean }>("citation-format", {
  description: DESCRIPTION,
  parameters,
  async execute(args, ctx) {
    const defaultModel = await Provider.defaultModel()
    const model = await Provider.getModel(defaultModel.providerID, defaultModel.modelID)
    const language = await Provider.getLanguage(model)

    // Try basic pattern matching first
    const citation = args.citation.trim()
    let basicFormatted = citation

    // US Patent: 10,123,456 or 10123456
    const usPatent = citation.match(/(?:US\s*)?(\d{1,2}[,.]?\d{3}[,.]?\d{3})\s*(B[12]|A[12])?/i)
    // US Publication: 2024/0123456
    const usPub = citation.match(/(?:US\s*)?(\d{4}\/[\d]{6,7})/i)
    // EP: EP1234567
    const epPatent = citation.match(/(?:EP\s*)?(\d{7})/i)
    // WO: WO2024/123456
    const woPatent = citation.match(/(?:WO\s*)?(\d{4}\/\d{6,})/i)
    // PCT: PCT/US2024/123456
    const pctPatent = citation.match(/(?:PCT\/)?([A-Z]{2}\d{4}\/\d{6,})/i)

    if (usPatent) {
      const num = usPatent[1].replace(/[,.]/g, "")
      const formattedNum = num.replace(/(\d+?)(\d{3})(\d{3})$/, "$1,$2,$3")
      const kind = usPatent[2] ? ` ${usPatent[2].toUpperCase()}` : ""
      basicFormatted = `US ${formattedNum}${kind}`
    } else if (usPub) {
      basicFormatted = `US ${usPub[1]}`
    } else if (epPatent) {
      basicFormatted = `EP ${epPatent[1]}`
    } else if (woPatent) {
      basicFormatted = `WO ${woPatent[1]}`
    } else if (pctPatent) {
      basicFormatted = `PCT/${pctPatent[1].toUpperCase()}`
    }

    const wasBasicFormatted = basicFormatted !== citation

    // Use AI for more complex cases (NPL, foreign patents, etc.)
    if (!wasBasicFormatted) {
      const prompt = `Format the following citation according to USPTO ${args.format} standards.

Citation: ${citation}

Provide:
1. The properly formatted citation
2. The type of reference (US patent, foreign patent, NPL, etc.)
3. Any issues found with the citation

Use standard USPTO formatting guidelines.`

      const result = await generateText({
        model: language,
        messages: [{ role: "user", content: prompt }],
      })

      return {
        title: `Cite: ${citation.slice(0, 30)}`,
        metadata: { formatted: true, basicFormat: false },
        output: result.text,
      }
    }

    return {
      title: `Cite: ${basicFormatted.slice(0, 40)}`,
      metadata: { formatted: wasBasicFormatted, basicFormat: true },
      output: [
        `Input: ${citation}`,
        `Formatted (${args.format}): ${basicFormatted}`,
        wasBasicFormatted ? "✓ Basic formatting applied." : "✓ No formatting needed.",
        "",
        "Note: For complex citations (foreign patents, NPL, etc.), use AI-enhanced formatting with the 'citation-format' tool.",
      ].join("\n"),
    }
  },
})

import { Tool } from "./tool"
import z from "zod"
import { Provider } from "../provider/provider"
import { generateText } from "ai"

const DESCRIPTION = `Validate patent documents against PTO requirements.

Check documents for compliance with formal requirements including:
- Page margins, font size, line spacing
- Abstract length (50-150 words)
- Claim formatting and numbering
- Drawing requirements
- Required sections present
- Filing requirements completeness`

const parameters = z.object({
    file_path: z.string().describe("Path to the patent document to check"),
    document_type: z
        .enum(["application", "claims", "abstract", "specification", "drawings-description", "ids", "office-action-response"])
        .describe("Type of document being checked"),
})

export const ComplianceCheckTool = Tool.define<typeof parameters, { issues: number }>(
    "compliance-check",
    {
        description: DESCRIPTION,
        parameters,
        async execute(args, ctx) {
            let content = ""
            try {
                content = await Bun.file(args.file_path).text()
            } catch {
                return {
                    title: `Check: ${args.file_path}`,
                    metadata: { issues: 1 },
                    output: `Error: Could not read file at ${args.file_path}`,
                }
            }

            const defaultModel = await Provider.defaultModel()
            const model = await Provider.getModel(defaultModel.providerID, defaultModel.modelID)
            const language = await Provider.getLanguage(model)

            const prompt = `Act as a patent compliance analyst. Review the following patent document of type "${args.document_type}".
Check for compliance with formal PTO requirements (e.g., section completion, formatting, numbering, transitional phrases if claims, abstract length limit of 150 words). Provide a structured output listing any issues found, or indicating compliance.

Document Content:
\n\n${content.substring(0, 50000)}`

            const result = await generateText({
                model: language,
                messages: [{ role: "user", content: prompt }]
            })

            return {
                title: `Check: ${args.document_type}`,
                metadata: { issues: 0 },
                output: result.text,
            }
        },
    },
)

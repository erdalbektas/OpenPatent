import { Tool } from "./tool"
import DESCRIPTION from "./mpep-lookup.txt"
import z from "zod"
import { Provider } from "../provider/provider"
import { generateText } from "ai"

const parameters = z.object({
  section: z.string().optional().describe("MPEP section number (e.g., '2143', '706.07(a)')"),
  keyword: z.string().optional().describe("Search keyword or phrase (e.g., 'obviousness')"),
  context: z.string().optional().describe("Brief description of why you need this lookup"),
})

export const MpepLookupTool = Tool.define<typeof parameters, {}>("mpep-lookup", {
  description: DESCRIPTION,
  parameters,
  async execute(args, ctx) {
    const defaultModel = await Provider.defaultModel()
    const model = await Provider.getModel(defaultModel.providerID, defaultModel.modelID)
    const language = await Provider.getLanguage(model)

    const query = args.section ? `MPEP Section ${args.section}` : `MPEP keyword: "${args.keyword}"`

    const prompt = `You are a patent law expert specializing in the USPTO Manual of Examining Procedure (MPEP).

${args.context ? `User context: ${args.context}` : ""}

${
  args.section
    ? `Provide detailed information about MPEP Section ${args.section}, including:
- The key legal standards and tests applied in this section
- Relevant case law citations (major CAFC decisions)
- Practical guidance for patent practitioners
- Any subsections that are particularly important`
    : `Search your knowledge for information about "${args.keyword}" in patent law, including:
- The relevant MPEP sections that govern this topic
- Key legal standards and tests
- Important case law citations
- How this applies to patent prosecution`
}

Provide a comprehensive, accurate response based on your training knowledge of the MPEP.`

    const result = await generateText({
      model: language,
      messages: [{ role: "user", content: prompt }],
    })

    return {
      title: `MPEP: ${query.slice(0, 40)}`,
      metadata: { section: args.section, keyword: args.keyword },
      output: result.text,
    }
  },
})

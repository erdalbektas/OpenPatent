import { Tool } from "./tool"
import DESCRIPTION from "./patent-search.txt"
import z from "zod"
import { Provider } from "../provider/provider"
import { generateText } from "ai"

const parameters = z.object({
  query: z
    .string()
    .describe("Search query — keywords, patent classifications (CPC/IPC), inventor names, or assignee names"),
  database: z
    .enum(["all", "uspto", "epo", "wipo", "google-patents"])
    .default("all")
    .describe("Which patent database to search"),
  date_range: z.string().optional().describe("Date range to limit results (e.g., '2020-2024')"),
  max_results: z.number().int().positive().default(20).describe("Maximum number of results to return"),
  classification: z.string().optional().describe("CPC or IPC classification code (e.g., H01L, G06F')"),
  inventor: z.string().optional().describe("Inventor name"),
  assignee: z.string().optional().describe("Assignee/company name"),
})

export const PatentSearchTool = Tool.define<typeof parameters, { resultCount: number }>("patent-search", {
  description: DESCRIPTION,
  parameters,
  async execute(args, ctx) {
    const defaultModel = await Provider.defaultModel()
    const model = await Provider.getModel(defaultModel.providerID, defaultModel.modelID)
    const language = await Provider.getLanguage(model)

    const searchDetails = [
      `Query: "${args.query}"`,
      args.classification ? `Classification: ${args.classification}` : null,
      args.inventor ? `Inventor: ${args.inventor}` : null,
      args.assignee ? `Assignee: ${args.assignee}` : null,
      `Database: ${args.database}`,
      args.date_range ? `Date range: ${args.date_range}` : null,
      `Max results: ${args.max_results}`,
    ]
      .filter(Boolean)
      .join("\n")

    const prompt = `You are a patent search expert. Based on your knowledge of patent databases and the patent landscape, provide a comprehensive prior art search report for:

${searchDetails}

For each relevant patent or reference found, provide:
- Patent/Publication number
- Title
- Inventor(s)
- Assignee
- Date
- Key technical disclosures relevant to: "${args.query}"

Also provide:
1. Summary of the overall patent landscape
2. Key players/companies in this technology area
3. Potential blocking patents that might affect freedom to operate
4. Suggestions for improving the search strategy

Be as thorough as possible given your knowledge. If you don't have specific patent numbers, provide general guidance on what types of patents would be relevant and how to find them.`

    const result = await generateText({
      model: language,
      messages: [{ role: "user", content: prompt }],
    })

    return {
      title: `Search: ${args.query.slice(0, 50)}`,
      metadata: {
        resultCount: args.max_results,
        database: args.database,
        query: args.query,
      },
      output: result.text,
    }
  },
})

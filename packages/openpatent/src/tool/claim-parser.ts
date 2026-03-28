import { Tool } from "./tool"
import DESCRIPTION from "./claim-parser.txt"
import z from "zod"

const parameters = z.object({
    claims_text: z.string().optional().describe("Raw claim text to parse"),
    file_path: z.string().optional().describe("Path to a file containing patent claims"),
})

export const ClaimParserTool = Tool.define<typeof parameters, { claimCount: number }>(
    "claim-parser",
    {
        description: DESCRIPTION,
        parameters,
        async execute(args, ctx) {
            const text = args.claims_text ?? (args.file_path ? await Bun.file(args.file_path).text() : "")
            if (!text.trim()) {
                return {
                    title: "No claims provided",
                    metadata: { claimCount: 0 },
                    output: "Error: Please provide either claims_text or file_path containing patent claims.",
                }
            }

            const claimPattern = /(?:^|\n)\s*(?:claim\s+)?(\d+)\.\s+([\s\S]*?)(?=(?:\n\s*(?:claim\s+)?\d+\.\s+)|$)/gi;
            const claims = [];
            let match;

            while ((match = claimPattern.exec(text)) !== null) {
                const claimNum = match[1];
                let body = match[2].trim();

                // Heuristic for preamble and transition
                const transitionMatch = body.match(/^(.*?)(comprising|consisting of|consisting essentially of|including|having|characterized by)([\s\S]*)$/i);

                if (transitionMatch) {
                    claims.push({
                        number: claimNum,
                        preamble: transitionMatch[1].trim(),
                        transition: transitionMatch[2].trim(),
                        elements: transitionMatch[3].trim()
                    });
                } else {
                    claims.push({
                        number: claimNum,
                        body: body
                    });
                }
            }

            const claimCount = claims.length;
            const output = JSON.stringify(claims, null, 2);

            return {
                title: `Parse ${claimCount} claim(s)`,
                metadata: { claimCount },
                output,
            }
        },
    },
)

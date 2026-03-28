import { Tool } from "./tool"
import z from "zod"
import { Provider } from "../provider/provider"
import { generateText } from "ai"

const DESCRIPTION = `Generate patent documents from standard templates.

Create properly formatted patent documents following PTO requirements.
Templates include: utility application, provisional application, PCT, 
continuation, CIP, divisional, office action response, IDS, and more.`

const TEMPLATE_INFO: Record<string, { description: string; sections: string[] }> = {
  "utility-application": {
    description: "Utility patent application (non-provisional)",
    sections: [
      "Title",
      "Cross-Reference",
      "Field of Invention",
      "Background",
      "Summary",
      "Brief Description of Drawings",
      "Detailed Description",
      "Claims",
      "Abstract",
    ],
  },
  "provisional-application": {
    description: "Provisional patent application",
    sections: [
      "Title",
      "Cross-Reference",
      "Field of Invention",
      "Background",
      "Summary",
      "Brief Description of Drawings",
      "Detailed Description",
      "Claims (optional)",
      "Abstract",
    ],
  },
  "pct-application": {
    description: "Patent Cooperation Treaty international application",
    sections: [
      "Title",
      "International Search Report reference",
      "Field of Invention",
      "Background",
      "Summary",
      "Brief Description of Drawings",
      "Detailed Description",
      "Claims",
      "Abstract",
    ],
  },
  continuation: {
    description: "Continuation of a pending application",
    sections: [
      "Title",
      "Cross-Reference to Related Applications",
      "Field of Invention",
      "Background",
      "Summary",
      "Brief Description of Drawings",
      "Detailed Description",
      "Claims",
      "Abstract",
    ],
  },
  cip: {
    description: "Continuation-in-part of a pending application",
    sections: [
      "Title",
      "Cross-Reference to Related Applications",
      "Field of Invention",
      "Background",
      "Summary",
      "Brief Description of Drawings",
      "Detailed Description",
      "Claims",
      "Abstract",
    ],
  },
  divisional: {
    description: "Divisional application from a parent",
    sections: [
      "Title",
      "Cross-Reference to Related Applications",
      "Field of Invention",
      "Background",
      "Summary",
      "Brief Description of Drawings",
      "Detailed Description",
      "Claims",
      "Abstract",
    ],
  },
  "office-action-response": {
    description: "Response to USPTO office action",
    sections: [
      "Amendment Summary",
      "Rejections Under 35 USC §101",
      "Rejections Under 35 USC §102",
      "Rejections Under 35 USC §103",
      "Rejections Under 35 USC §112",
      "Remarks/Arguments",
    ],
  },
  ids: {
    description: "Information Disclosure Statement",
    sections: ["List of Cited References", "Foreign Patent Documents", "Non-Patent Literature", "Certification"],
  },
  declaration: {
    description: "Inventor's declaration under 37 CFR 1.63",
    sections: ["Inventor Identification", "Declaration Statement", "Acknowledgment", "Execution Date"],
  },
  assignment: {
    description: "Assignment of patent rights",
    sections: ["Parties", "Recitals", "Assignment Terms", "Signature Blocks", "Recording Information"],
  },
  "power-of-attorney": {
    description: "Power of attorney for patent matters",
    sections: ["Principal Authorization", "Attorney Information", "Signature", "Date"],
  },
}

const parameters = z.object({
  template: z
    .enum([
      "utility-application",
      "provisional-application",
      "pct-application",
      "continuation",
      "cip",
      "divisional",
      "office-action-response",
      "ids",
      "declaration",
      "assignment",
      "power-of-attorney",
    ])
    .describe("The type of patent document template to generate"),
  invention_title: z.string().optional().describe("Title of the invention"),
  applicant: z.string().optional().describe("Applicant name (for applications)"),
  inventor: z.string().optional().describe("Inventor name(s)"),
  application_number: z.string().optional().describe("Existing application number (for continuations/responses)"),
  notes: z.string().optional().describe("Additional instructions or notes for the template"),
  field_of_invention: z.string().optional().describe("Brief description of the technical field"),
  background: z.string().optional().describe("Background of the invention description"),
})

export const DocumentTemplateTool = Tool.define<typeof parameters, { template: string }>("document-template", {
  description: DESCRIPTION,
  parameters,
  async execute(args, ctx) {
    const templateInfo = TEMPLATE_INFO[args.template]

    const defaultModel = await Provider.defaultModel()
    const model = await Provider.getModel(defaultModel.providerID, defaultModel.modelID)
    const language = await Provider.getLanguage(model)

    const prompt = `Generate a ${templateInfo.description} template.

${args.invention_title ? `Invention Title: ${args.invention_title}` : "[Provide invention title]"}
${args.applicant ? `Applicant: ${args.applicant}` : "[Provide applicant name]"}
${args.inventor ? `Inventor(s): ${args.inventor}` : "[Provide inventor name(s)]"}
${args.application_number ? `Related Application: ${args.application_number}` : ""}
${args.field_of_invention ? `Technical Field: ${args.field_of_invention}` : ""}
${args.background ? `Background: ${args.background}` : ""}

Required sections:
${templateInfo.sections.map((s) => `- ${s}`).join("\n")}

${args.notes ? `Additional Notes: ${args.notes}` : ""}

Generate a complete, properly formatted patent document template with:
- All standard section headings
- Bracketed placeholders [like this] for required information
- Guidance comments in italics where needed
- Proper patent terminology and formatting

Use standard USPTO formatting (12pt Times New Roman, 1.0 line spacing, 1-inch margins).`

    const result = await generateText({
      model: language,
      messages: [{ role: "user", content: prompt }],
    })

    return {
      title: `Template: ${args.template}`,
      metadata: { template: args.template, sections: templateInfo.sections.length },
      output: result.text,
    }
  },
})

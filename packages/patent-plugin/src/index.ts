import { Plugin } from "@opencode/plugin"
import { Agent } from "@opencode/schema/agent"
import { patentAgents, PATENT_AGENT_IDS } from "./agents"
import { registerPatentTools } from "./tools"

export default Plugin.define({
  id: "openpatent",
  async setup(ctx) {
    await ctx.agent.transform((editor) => {
      for (const id of PATENT_AGENT_IDS) {
        const def = patentAgents[id]
        editor.update(def.info.id, (agent) => {
          Object.assign(agent, def.info)
          agent.system = def.system
        })
      }
      editor.default(Agent.ID.make("counsel"))
    })

    await ctx.tool.transform((editor) => {
      registerPatentTools(editor)
    })
  },
})

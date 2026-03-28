import { cmd } from "./cmd"
import * as prompts from "@clack/prompts"
import { UI } from "../ui"
import { Global } from "../../global"
import { Agent, canUseAgent, getUserPlan, PlanTier, PAID_AGENTS } from "../../agent/agent"
import { Provider } from "../../provider/provider"
import { OpenPatentAuth } from "../../auth/openpatent"
import path from "path"
import fs from "fs/promises"
import { Filesystem } from "../../util/filesystem"
import matter from "gray-matter"
import { Instance } from "../../project/instance"
import { EOL } from "os"
import type { Argv } from "yargs"

type AgentMode = "all" | "primary" | "subagent"

const AVAILABLE_TOOLS = [
  "bash",
  "read",
  "write",
  "edit",
  "list",
  "glob",
  "grep",
  "webfetch",
  "task",
  "todowrite",
  "todoread",
]

const AgentCreateCommand = cmd({
  command: "create",
  describe: "create a new agent",
  builder: (yargs: Argv) =>
    yargs
      .option("path", {
        type: "string",
        describe: "directory path to generate the agent file",
      })
      .option("description", {
        type: "string",
        describe: "what the agent should do",
      })
      .option("mode", {
        type: "string",
        describe: "agent mode",
        choices: ["all", "primary", "subagent"] as const,
      })
      .option("tools", {
        type: "string",
        describe: `comma-separated list of tools to enable (default: all). Available: "${AVAILABLE_TOOLS.join(", ")}"`,
      })
      .option("model", {
        type: "string",
        alias: ["m"],
        describe: "model to use in the format of provider/model",
      }),
  async handler(args) {
    await Instance.provide({
      directory: process.cwd(),
      async fn() {
        const cliPath = args.path
        const cliDescription = args.description
        const cliMode = args.mode as AgentMode | undefined
        const cliTools = args.tools

        const isFullyNonInteractive = cliPath && cliDescription && cliMode && cliTools !== undefined

        if (!isFullyNonInteractive) {
          UI.empty()
          prompts.intro("Create agent")
        }

        const project = Instance.project

        // Determine scope/path
        let targetPath: string
        if (cliPath) {
          targetPath = path.join(cliPath, "agent")
        } else {
          let scope: "global" | "project" = "global"
          if (project.vcs === "git") {
            const scopeResult = await prompts.select({
              message: "Location",
              options: [
                {
                  label: "Current project",
                  value: "project" as const,
                  hint: Instance.worktree,
                },
                {
                  label: "Global",
                  value: "global" as const,
                  hint: Global.Path.config,
                },
              ],
            })
            if (prompts.isCancel(scopeResult)) throw new UI.CancelledError()
            scope = scopeResult
          }
          targetPath = path.join(
            scope === "global" ? Global.Path.config : path.join(Instance.worktree, ".openpatent"),
            "agent",
          )
        }

        // Get description
        let description: string
        if (cliDescription) {
          description = cliDescription
        } else {
          const query = await prompts.text({
            message: "Description",
            placeholder: "What should this agent do?",
            validate: (x) => (x && x.length > 0 ? undefined : "Required"),
          })
          if (prompts.isCancel(query)) throw new UI.CancelledError()
          description = query
        }

        // Generate agent
        const spinner = prompts.spinner()
        spinner.start("Generating agent configuration...")
        const model = args.model ? Provider.parseModel(args.model) : undefined
        const generated = await Agent.generate({ description, model }).catch((error) => {
          spinner.stop(`LLM failed to generate agent: ${error.message}`, 1)
          if (isFullyNonInteractive) process.exit(1)
          throw new UI.CancelledError()
        })
        spinner.stop(`Agent ${generated.identifier} generated`)

        // Select tools
        let selectedTools: string[]
        if (cliTools !== undefined) {
          selectedTools = cliTools ? cliTools.split(",").map((t) => t.trim()) : AVAILABLE_TOOLS
        } else {
          const result = await prompts.multiselect({
            message: "Select tools to enable (Space to toggle)",
            options: AVAILABLE_TOOLS.map((tool) => ({
              label: tool,
              value: tool,
            })),
            initialValues: AVAILABLE_TOOLS,
          })
          if (prompts.isCancel(result)) throw new UI.CancelledError()
          selectedTools = result
        }

        // Get mode
        let mode: AgentMode
        if (cliMode) {
          mode = cliMode
        } else {
          const modeResult = await prompts.select({
            message: "Agent mode",
            options: [
              {
                label: "All",
                value: "all" as const,
                hint: "Can function in both primary and subagent roles",
              },
              {
                label: "Primary",
                value: "primary" as const,
                hint: "Acts as a primary/main agent",
              },
              {
                label: "Subagent",
                value: "subagent" as const,
                hint: "Can be used as a subagent by other agents",
              },
            ],
            initialValue: "all" as const,
          })
          if (prompts.isCancel(modeResult)) throw new UI.CancelledError()
          mode = modeResult
        }

        // Build tools config
        const tools: Record<string, boolean> = {}
        for (const tool of AVAILABLE_TOOLS) {
          if (!selectedTools.includes(tool)) {
            tools[tool] = false
          }
        }

        // Build frontmatter
        const frontmatter: {
          description: string
          mode: AgentMode
          tools?: Record<string, boolean>
        } = {
          description: generated.whenToUse,
          mode,
        }
        if (Object.keys(tools).length > 0) {
          frontmatter.tools = tools
        }

        // Write file
        const content = matter.stringify(generated.systemPrompt, frontmatter)
        const filePath = path.join(targetPath, `${generated.identifier}.md`)

        await fs.mkdir(targetPath, { recursive: true })

        if (await Filesystem.exists(filePath)) {
          if (isFullyNonInteractive) {
            console.error(`Error: Agent file already exists: ${filePath}`)
            process.exit(1)
          }
          prompts.log.error(`Agent file already exists: ${filePath}`)
          throw new UI.CancelledError()
        }

        await Filesystem.write(filePath, content)

        if (isFullyNonInteractive) {
          console.log(filePath)
        } else {
          prompts.log.success(`Agent created: ${filePath}`)
          prompts.outro("Done")
        }
      },
    })
  },
})

const AgentListCommand = cmd({
  command: "list",
  aliases: ["ls"],
  describe: "list all available agents with plan info",
  async handler() {
    UI.empty()
    prompts.intro("Available Agents")

    const userPlan = await getUserPlan()
    const auth = await OpenPatentAuth.get()
    const isAuthenticated = !!auth && (await OpenPatentAuth.isValid())

    prompts.log.info(`Your plan: ${userPlan.toUpperCase()}`)
    if (!isAuthenticated) {
      prompts.log.info(`Run 'openpatent auth openpatent login' to authenticate`)
    }
    prompts.log.info("")

    const agents = await Agent.list()
    const sortedAgents = agents
      .filter((a) => !a.hidden)
      .sort((a, b) => {
        if (a.native !== b.native) return a.native ? -1 : 1
        return a.name.localeCompare(b.name)
      })

    const isPaid = (name: string) => PAID_AGENTS.has(name)
    const getPlanBadge = (name: string, plan: PlanTier): string => {
      if (!isPaid(name)) return UI.Style.TEXT_DIM + "(free)"
      if (plan === "enterprise") return UI.Style.TEXT_SUCCESS + "(enterprise)"
      if (plan === "pro") return UI.Style.TEXT_SUCCESS + "(pro)"
      return UI.Style.TEXT_WARNING + "(premium)"
    }

    const primaryAgents = sortedAgents.filter((a) => a.mode === "primary")
    const subAgents = sortedAgents.filter((a) => a.mode === "subagent")

    prompts.log.info(UI.Style.TEXT_INFO_BOLD + "Primary Agents:")
    for (const agent of primaryAgents) {
      const badge = getPlanBadge(agent.name, userPlan)
      prompts.log.info(`  ${agent.name} ${badge} ${UI.Style.TEXT_DIM}- ${agent.description || ""}`)
    }

    prompts.log.info("")
    prompts.log.info(UI.Style.TEXT_INFO_BOLD + "Subagents:")
    for (const agent of subAgents) {
      const badge = getPlanBadge(agent.name, userPlan)
      prompts.log.info(`  ${agent.name} ${badge} ${UI.Style.TEXT_DIM}- ${agent.description || ""}`)
    }

    if (userPlan === "free" && !isAuthenticated) {
      prompts.log.info("")
      prompts.log.info(UI.Style.TEXT_INFO_BOLD + "Premium agents require authentication.")
      prompts.log.info(`Run 'openpatent auth openpatent login' to unlock all agents,`)
      prompts.log.info(`or visit https://openpatent.techtank.com.tr to upgrade.`)
    }

    prompts.outro(`${sortedAgents.length} agents`)
  },
})

export const AgentCommand = cmd({
  command: "agent",
  describe: "manage agents",
  builder: (yargs) => yargs.command(AgentCreateCommand).command(AgentListCommand).demandCommand(),
  async handler() {},
})

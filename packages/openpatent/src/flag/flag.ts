function truthy(key: string) {
  const value = process.env[key]?.toLowerCase()
  return value === "true" || value === "1"
}

export namespace Flag {
  export const OPENPATENT_AUTO_SHARE = truthy("OPENPATENT_AUTO_SHARE")
  export const OPENPATENT_GIT_BASH_PATH = process.env["OPENPATENT_GIT_BASH_PATH"]
  export const OPENPATENT_CONFIG = process.env["OPENPATENT_CONFIG"]
  export declare const OPENPATENT_TUI_CONFIG: string | undefined
  export declare const OPENPATENT_CONFIG_DIR: string | undefined
  export const OPENPATENT_CONFIG_CONTENT = process.env["OPENPATENT_CONFIG_CONTENT"]
  export const OPENPATENT_DISABLE_AUTOUPDATE = truthy("OPENPATENT_DISABLE_AUTOUPDATE")
  export const OPENPATENT_DISABLE_PRUNE = truthy("OPENPATENT_DISABLE_PRUNE")
  export const OPENPATENT_DISABLE_TERMINAL_TITLE = truthy("OPENPATENT_DISABLE_TERMINAL_TITLE")
  export const OPENPATENT_PERMISSION = process.env["OPENPATENT_PERMISSION"]
  export const OPENPATENT_DISABLE_DEFAULT_PLUGINS = truthy("OPENPATENT_DISABLE_DEFAULT_PLUGINS")
  export const OPENPATENT_DISABLE_LSP_DOWNLOAD = truthy("OPENPATENT_DISABLE_LSP_DOWNLOAD")
  export const OPENPATENT_ENABLE_EXPERIMENTAL_MODELS = truthy("OPENPATENT_ENABLE_EXPERIMENTAL_MODELS")
  export const OPENPATENT_DISABLE_AUTOCOMPACT = truthy("OPENPATENT_DISABLE_AUTOCOMPACT")
  export const OPENPATENT_DISABLE_MODELS_FETCH = truthy("OPENPATENT_DISABLE_MODELS_FETCH")
  export const OPENPATENT_DISABLE_CLAUDE_CODE = truthy("OPENPATENT_DISABLE_CLAUDE_CODE")
  export const OPENPATENT_DISABLE_CLAUDE_CODE_PROMPT =
    OPENPATENT_DISABLE_CLAUDE_CODE || truthy("OPENPATENT_DISABLE_CLAUDE_CODE_PROMPT")
  export const OPENPATENT_DISABLE_CLAUDE_CODE_SKILLS =
    OPENPATENT_DISABLE_CLAUDE_CODE || truthy("OPENPATENT_DISABLE_CLAUDE_CODE_SKILLS")
  export const OPENPATENT_DISABLE_EXTERNAL_SKILLS =
    OPENPATENT_DISABLE_CLAUDE_CODE_SKILLS || truthy("OPENPATENT_DISABLE_EXTERNAL_SKILLS")
  export declare const OPENPATENT_DISABLE_PROJECT_CONFIG: boolean
  export const OPENPATENT_FAKE_VCS = process.env["OPENPATENT_FAKE_VCS"]
  export declare const OPENPATENT_CLIENT: string
  export const OPENPATENT_SERVER_PASSWORD = process.env["OPENPATENT_SERVER_PASSWORD"]
  export const OPENPATENT_SERVER_USERNAME = process.env["OPENPATENT_SERVER_USERNAME"]
  export const OPENPATENT_ENABLE_QUESTION_TOOL = truthy("OPENPATENT_ENABLE_QUESTION_TOOL")

  // Experimental
  export const OPENPATENT_EXPERIMENTAL = truthy("OPENPATENT_EXPERIMENTAL")
  export const OPENPATENT_EXPERIMENTAL_FILEWATCHER = truthy("OPENPATENT_EXPERIMENTAL_FILEWATCHER")
  export const OPENPATENT_EXPERIMENTAL_DISABLE_FILEWATCHER = truthy("OPENPATENT_EXPERIMENTAL_DISABLE_FILEWATCHER")
  export const OPENPATENT_EXPERIMENTAL_ICON_DISCOVERY =
    OPENPATENT_EXPERIMENTAL || truthy("OPENPATENT_EXPERIMENTAL_ICON_DISCOVERY")

  const copy = process.env["OPENPATENT_EXPERIMENTAL_DISABLE_COPY_ON_SELECT"]
  export const OPENPATENT_EXPERIMENTAL_DISABLE_COPY_ON_SELECT =
    copy === undefined ? process.platform === "win32" : truthy("OPENPATENT_EXPERIMENTAL_DISABLE_COPY_ON_SELECT")
  export const OPENPATENT_ENABLE_EXA =
    truthy("OPENPATENT_ENABLE_EXA") || OPENPATENT_EXPERIMENTAL || truthy("OPENPATENT_EXPERIMENTAL_EXA")
  export const OPENPATENT_EXPERIMENTAL_BASH_DEFAULT_TIMEOUT_MS = number("OPENPATENT_EXPERIMENTAL_BASH_DEFAULT_TIMEOUT_MS")
  export const OPENPATENT_EXPERIMENTAL_OUTPUT_TOKEN_MAX = number("OPENPATENT_EXPERIMENTAL_OUTPUT_TOKEN_MAX")
  export const OPENPATENT_EXPERIMENTAL_OXFMT = OPENPATENT_EXPERIMENTAL || truthy("OPENPATENT_EXPERIMENTAL_OXFMT")
  export const OPENPATENT_EXPERIMENTAL_LSP_TY = truthy("OPENPATENT_EXPERIMENTAL_LSP_TY")
  export const OPENPATENT_EXPERIMENTAL_LSP_TOOL = OPENPATENT_EXPERIMENTAL || truthy("OPENPATENT_EXPERIMENTAL_LSP_TOOL")
  export const OPENPATENT_DISABLE_FILETIME_CHECK = truthy("OPENPATENT_DISABLE_FILETIME_CHECK")
  export const OPENPATENT_EXPERIMENTAL_PLAN_MODE = OPENPATENT_EXPERIMENTAL || truthy("OPENPATENT_EXPERIMENTAL_PLAN_MODE")
  export const OPENPATENT_EXPERIMENTAL_MARKDOWN = truthy("OPENPATENT_EXPERIMENTAL_MARKDOWN")
  export const OPENPATENT_MODELS_URL = process.env["OPENPATENT_MODELS_URL"]
  export const OPENPATENT_MODELS_PATH = process.env["OPENPATENT_MODELS_PATH"]

  function number(key: string) {
    const value = process.env[key]
    if (!value) return undefined
    const parsed = Number(value)
    return Number.isInteger(parsed) && parsed > 0 ? parsed : undefined
  }
}

// Dynamic getter for OPENPATENT_DISABLE_PROJECT_CONFIG
// This must be evaluated at access time, not module load time,
// because external tooling may set this env var at runtime
Object.defineProperty(Flag, "OPENPATENT_DISABLE_PROJECT_CONFIG", {
  get() {
    return truthy("OPENPATENT_DISABLE_PROJECT_CONFIG")
  },
  enumerable: true,
  configurable: false,
})

// Dynamic getter for OPENPATENT_TUI_CONFIG
// This must be evaluated at access time, not module load time,
// because tests and external tooling may set this env var at runtime
Object.defineProperty(Flag, "OPENPATENT_TUI_CONFIG", {
  get() {
    return process.env["OPENPATENT_TUI_CONFIG"]
  },
  enumerable: true,
  configurable: false,
})

// Dynamic getter for OPENPATENT_CONFIG_DIR
// This must be evaluated at access time, not module load time,
// because external tooling may set this env var at runtime
Object.defineProperty(Flag, "OPENPATENT_CONFIG_DIR", {
  get() {
    return process.env["OPENPATENT_CONFIG_DIR"]
  },
  enumerable: true,
  configurable: false,
})

// Dynamic getter for OPENPATENT_CLIENT
// This must be evaluated at access time, not module load time,
// because some commands override the client at runtime
Object.defineProperty(Flag, "OPENPATENT_CLIENT", {
  get() {
    return process.env["OPENPATENT_CLIENT"] ?? "cli"
  },
  enumerable: true,
  configurable: false,
})

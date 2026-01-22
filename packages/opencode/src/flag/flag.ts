export namespace Flag {
  export const openpatent_AUTO_SHARE = truthy("openpatent_AUTO_SHARE")
  export const openpatent_GIT_BASH_PATH = process.env["openpatent_GIT_BASH_PATH"]
  export const openpatent_CONFIG = process.env["openpatent_CONFIG"]
  export const openpatent_CONFIG_DIR = process.env["openpatent_CONFIG_DIR"]
  export const openpatent_CONFIG_CONTENT = process.env["openpatent_CONFIG_CONTENT"]
  export const openpatent_DISABLE_AUTOUPDATE = truthy("openpatent_DISABLE_AUTOUPDATE")
  export const openpatent_DISABLE_PRUNE = truthy("openpatent_DISABLE_PRUNE")
  export const openpatent_DISABLE_TERMINAL_TITLE = truthy("openpatent_DISABLE_TERMINAL_TITLE")
  export const openpatent_PERMISSION = process.env["openpatent_PERMISSION"]
  export const openpatent_DISABLE_DEFAULT_PLUGINS = truthy("openpatent_DISABLE_DEFAULT_PLUGINS")
  export const openpatent_DISABLE_LSP_DOWNLOAD = truthy("openpatent_DISABLE_LSP_DOWNLOAD")
  export const openpatent_ENABLE_EXPERIMENTAL_MODELS = truthy("openpatent_ENABLE_EXPERIMENTAL_MODELS")
  export const openpatent_DISABLE_AUTOCOMPACT = truthy("openpatent_DISABLE_AUTOCOMPACT")
  export const openpatent_DISABLE_MODELS_FETCH = truthy("openpatent_DISABLE_MODELS_FETCH")
  export const openpatent_FAKE_VCS = process.env["openpatent_FAKE_VCS"]
  export const openpatent_CLIENT = process.env["openpatent_CLIENT"] ?? "cli"

  // Experimental
  export const openpatent_EXPERIMENTAL = truthy("openpatent_EXPERIMENTAL")
  export const openpatent_EXPERIMENTAL_FILEWATCHER = truthy("openpatent_EXPERIMENTAL_FILEWATCHER")
  export const openpatent_EXPERIMENTAL_DISABLE_FILEWATCHER = truthy("openpatent_EXPERIMENTAL_DISABLE_FILEWATCHER")
  export const openpatent_EXPERIMENTAL_ICON_DISCOVERY =
    openpatent_EXPERIMENTAL || truthy("openpatent_EXPERIMENTAL_ICON_DISCOVERY")
  export const openpatent_EXPERIMENTAL_DISABLE_COPY_ON_SELECT = truthy("openpatent_EXPERIMENTAL_DISABLE_COPY_ON_SELECT")
  export const openpatent_ENABLE_EXA =
    truthy("openpatent_ENABLE_EXA") || openpatent_EXPERIMENTAL || truthy("openpatent_EXPERIMENTAL_EXA")
  export const openpatent_EXPERIMENTAL_BASH_MAX_OUTPUT_LENGTH = number("openpatent_EXPERIMENTAL_BASH_MAX_OUTPUT_LENGTH")
  export const openpatent_EXPERIMENTAL_BASH_DEFAULT_TIMEOUT_MS = number("openpatent_EXPERIMENTAL_BASH_DEFAULT_TIMEOUT_MS")
  export const openpatent_EXPERIMENTAL_OUTPUT_TOKEN_MAX = number("openpatent_EXPERIMENTAL_OUTPUT_TOKEN_MAX")
  export const openpatent_EXPERIMENTAL_OXFMT = openpatent_EXPERIMENTAL || truthy("openpatent_EXPERIMENTAL_OXFMT")
  export const openpatent_EXPERIMENTAL_LSP_TY = truthy("openpatent_EXPERIMENTAL_LSP_TY")
  export const openpatent_EXPERIMENTAL_LSP_TOOL = openpatent_EXPERIMENTAL || truthy("openpatent_EXPERIMENTAL_LSP_TOOL")

  function truthy(key: string) {
    const value = process.env[key]?.toLowerCase()
    return value === "true" || value === "1"
  }

  function number(key: string) {
    const value = process.env[key]
    if (!value) return undefined
    const parsed = Number(value)
    return Number.isInteger(parsed) && parsed > 0 ? parsed : undefined
  }
}

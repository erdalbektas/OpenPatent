# OpenPatent

**Local, open-source AI for patent drafting — run models, skills, and agents entirely on your computer, at no cost, forever.**

OpenPatent helps you draft and refine patent work where your invention data belongs: on your machine. The core is **MIT licensed**, the layout is **transparent** (you can read how agents and tools are wired), and you can use **your own** local or self-hosted models plus **your own** skills and automation — no subscription required for self-hosted use.

**Website:** [openpatent.techtank.com.tr](https://openpatent.techtank.com.tr)

## Download

Prebuilt installers (Windows, Linux, macOS) are published on GitHub:

**[Download the latest release](https://github.com/erdalbektas/OpenPatent/releases/latest)**

Building from source is also free and stays fully local-first — see [Getting started](#getting-started) below.

## Why OpenPatent

- **Local patent drafting** — Keep drafting, claims, and strategy work under your control when you use a local or self-hosted model endpoint.
- **Open source** — MIT license; inspect, fork, and adapt the code.
- **Transparent structure** — Core logic, agents, and patent tools live in plain view under `packages/openpatent` (see [Repository layout](#repository-layout)).
- **Free forever (self-hosted)** — No fee to run the open-source stack yourself; optional paid services elsewhere do not change that.
- **Your models, skills, and agents** — Plug in OpenAI-compatible local runtimes (e.g. Ollama, LM Studio) and extend behavior with your own skills and agents on your hardware.

Honest scope: some workflows may call out to **optional** external APIs (for example patent database or provider APIs) when you configure them. Your LLM and custom extensions can still run entirely locally.

## Built on OpenCode

OpenPatent is built on **[OpenCode](https://opencode.ai)** — the same agent-first, tool-rich foundation used for local AI workflows. Upstream project: [github.com/anomalyco/opencode](https://github.com/anomalyco/opencode).

## What you can do

- **Patent drafting** — Applications, claims, specifications, abstracts, and drawing descriptions from plain-language input.
- **Prosecution** — Office action responses, amendments, and arguments.
- **Consulting** — Patentability, FTO, landscape, and validity-style analysis (configure tools and data sources as needed).
- **Litigation support** — Claim construction, infringement and invalidity-oriented outputs.
- **Portfolio management** — Docket-style tracking, deadlines, and status summaries.
- **Strategic planning** — Landscape and claim strategy support.

Primary workflow agents include `draft`, `prosecute`, `consult`, `litigate`, `manage`, and `strategy`. Specialist subagents (for example `prior-art`, `analyst`, `claims-analyst`) are available through task delegation. Patent-oriented tools include `patent-search`, `claim-parser`, `mpep-lookup`, `docket-query`, `document-template`, `compliance-check`, and `citation-format`.

## Getting started

### Download Directly

**[Download the latest release](https://github.com/erdalbektas/OpenPatent/releases/latest)**


### Build yourself

- [Bun](https://bun.sh/) 1.3+
- A model endpoint — **recommended for zero ongoing API cost:** a local OpenAI-compatible server (Ollama, LM Studio, vLLM, etc.). Cloud providers are optional.

### Install from source

```bash
git clone https://github.com/erdalbektas/OpenPatent.git
cd OpenPatent
bun install
bun dev
```

From the repo root, `bun dev` is the development equivalent of the `openpatent` CLI. For a standalone binary built locally:

```bash
./packages/openpatent/script/build.ts --single
./packages/openpatent/dist/openpatent-<platform>/bin/openpatent
```

### Configuration

**Local-first:** Select the local usage from providers menu to point OpenPatent at an OpenAI-compatible base URL (for example Ollama at `http://127.0.0.1:11434/v1`). 

To do that manually, put config in `openpatent.json` or `.openpatent/openpatent.json` in your project (or the paths described in [CONTRIBUTING.md](CONTRIBUTING.md)); the file supports `$schema` for validation.

**Optional cloud providers:** Also, you can configure hosted APIs (OpenAI, Anthropic, Google, and others) if you choose — that path is optional and not required for local-only use.

Example (local OpenAI-compatible server — adjust host, model selection, and API key rules for your runtime):

```json
{
  "$schema": "https://openpatent.ai/config.json",
  "provider": {
    "openai": {
      "options": {
        "apiKey": "ollama",
        "baseURL": "http://127.0.0.1:11434/v1"
      }
    }
  }
}
```

Environment variables are also supported for provider credentials where applicable.

## License

MIT

## Contact

**Tech Tank**  
Email: [openpatent@techtank.com.tr](mailto:openpatent@techtank.com.tr)

# OpenPatent

**Free, open-source, agentic AI for patent work — run on your machine with local models or any provider you choose.**

OpenPatent is an MIT-licensed patent office suite. Your invention data, your models, your wiki, your rules. No black box: agents, tools, and wiki logic live in plain source you can read, fork, and extend.

**Website:** [openpatent.techtank.com.tr](https://openpatent.techtank.com.tr)

---

## Download

Prebuilt installers are published on GitHub Releases:

**[Download the latest release](https://github.com/erdalbektas/openpatent/releases/latest)**

| Platform | Artifact |
|----------|----------|
| macOS (Apple Silicon + Intel) | `OpenPatent_<version>_universal.dmg` |
| Windows (x64) | `OpenPatent_<version>_x64-setup.exe` |
| Linux (x64) | `OpenPatent_<version>_amd64.deb` or `open-patent_<version>_amd64.AppImage` |

Each release includes the desktop app and the `openpatent` CLI sidecar. Building from source is also free — see [Build from source](#build-from-source).

---

## Why OpenPatent

### Free and open source

- **MIT license** — use, modify, and redistribute without restriction.
- **Transparent by design** — core logic lives under `packages/openpatent`; nothing is hidden behind proprietary glue.
- **Self-hosted forever** — run the full stack on your hardware at no software cost. Optional cloud APIs are your choice, not a requirement.

### Local models first

OpenPatent is built for **local inference**. Point it at any OpenAI-compatible endpoint and keep drafting, claims, and research on your network:

- [Ollama](https://ollama.com)
- [LM Studio](https://lmstudio.ai)
- [vLLM](https://github.com/vllm-project/vllm)
- Private or air-gapped runtimes

Local models mean your matter files, claim strategy, and prosecution notes never need to leave your machine.

### Any provider, your keys

OpenPatent is **model-agnostic**. Use local runtimes for zero API spend, or connect hosted providers when you want frontier models:

- OpenAI
- Anthropic
- Google
- OpenRouter and other OpenAI-compatible APIs

Switch models per agent, per session, or per task. Bring your own API keys — OpenPatent does not lock you into a single vendor.

### Agentic, not a chatbot

OpenPatent is an **agentic system**. In a session it:

- Reads and writes patent documents on disk
- Calls patent-specific tools (`patent-search`, `claim-parser`, `mpep-lookup`, `compliance-check`, and more)
- Delegates sub-tasks to specialist subagents
- Maintains context across a matter as work evolves

You describe the outcome; agents plan steps, invoke tools, and produce citation-backed drafts and analysis.

### Patent Wiki — persistent LLM memory

Patent work spans weeks. OpenPatent includes a **two-tier LLM wiki** so knowledge survives across sessions instead of vanishing when a chat ends.

```
Raw sources  →  wiki-ingest  →  Matter wiki (per project)
                                      ↓
                               review + lint
                                      ↓
                               wiki-promote  →  Master wiki (reusable doctrine)
                                      ↑
                               wiki-pull-master (import into new matters)
```

**Matter wiki** (`.openpatent/wiki/`) stores private, matter-specific knowledge — claim mappings, prior art notes, prosecution history, and ingested sources.

**Master wiki** stores **reusable, non-client** doctrine you approve once and pull into future matters.

Agents are instructed to **query the wiki before external search**. The `wiki-query` tool searches matter first, then master, returning tier-labeled snippets with file paths for citation-backed answers.

| Tool | Role |
|------|------|
| `wiki-ingest` | Build or refresh wiki pages from raw `.md`/`.txt` sources |
| `wiki-query` | Wiki-first retrieval for patent questions |
| `wiki-lint` | Schema, citation, and cross-link checks |
| `wiki-review` | Human review queue (`draft` → `reviewed` → `approved`) |
| `wiki-policy-report` | Promotion readiness and blocker report |
| `wiki-promote` | Copy approved matter pages into master wiki |
| `wiki-pull-master` | Import master doctrine into a matter without silent overwrite |

Wiki pages carry structured frontmatter (`review_status`, `confidentiality`, `promotion_state`, `source_ids`) so agents and humans share the same provenance rules. See `.openpatent/wiki/schema.md` for the full policy.

---

## What you can do

| Area | Examples |
|------|----------|
| **Drafting** | Applications, claims, specifications, abstracts, drawing descriptions |
| **Prosecution** | Office action responses, amendments, MPEP-grounded arguments |
| **Consulting** | Patentability, FTO, landscape, and validity-style analysis |
| **Prior art** | Database search, claim mapping, landscape synthesis |
| **Litigation** | Claim construction, infringement and invalidity contentions |
| **Portfolio** | Docket tracking, deadlines, status summaries |
| **Drawings** | USPTO-oriented flowcharts and system diagrams |

---

## Agents

### Primary workflow agents

| Agent | Purpose |
|-------|---------|
| `draft` | Default drafting — claims, specification, abstract |
| `prosecute` | Office actions, amendments, arguments |
| `consult` | Read-only consulting and opinions |
| `litigate` | Litigation support and claim construction |
| `manage` | Portfolio and docket management |
| `strategy` | Claim strategy and landscape planning |
| `draw` | Patent figure generation |

### Specialist subagents

Delegated automatically for focused work:

| Subagent | Purpose |
|----------|---------|
| `prior-art` | Multi-database prior art search and relevance analysis |
| `claims-analyst` | Claim parsing, element mapping, scope analysis |
| `legal-research` | MPEP, case law, and statute research (wiki-first) |
| `analyst` | Parallel multi-step research tasks |
| `document-writer` | Formal PTO-style document generation |
| `reviewer` | Compliance and claim-quality review |

Create custom agents with `openpatent agent create` — choose tools, model, and permissions for your practice.

---

## Quick start

### 1. Install from GitHub

Download the installer for your platform from **[GitHub Releases](https://github.com/erdalbektas/openpatent/releases/latest)** and open the app or CLI.

### 2. Connect a model

**Local (recommended):** start Ollama (or similar), then in OpenPatent select your local provider or add config:

```json
{
  "$schema": "https://openpatent.techtank.com.tr/config.json",
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

**Hosted:** add your provider API key via the providers menu or `openpatent.json` / `.openpatent/openpatent.json` in your project directory.

### 3. Open a matter and work

```bash
cd /path/to/your/matter
openpatent
```

Pick an agent (`draft`, `prosecute`, `consult`, …), describe the task, and let the agent use tools and the wiki as needed.

### 4. Seed the wiki (optional but powerful)

Drop source files under `.openpatent/wiki/raw/sources/`, then ask the agent to ingest them — or run ingest directly. Future sessions query that knowledge instead of starting from zero.

---

## Build from source

Requires [Bun](https://bun.sh/) 1.3+ and a model endpoint (local or hosted).

```bash
git clone https://github.com/erdalbektas/openpatent.git
cd openpatent
bun install
bun dev
```

`bun dev` from the repo root runs the development CLI. For a standalone binary:

```bash
./packages/openpatent/script/build.ts --single
./packages/openpatent/dist/openpatent-<platform>/bin/openpatent
```

Desktop app development:

```bash
bun run dev:desktop
```

---

## Configuration

Config file: `openpatent.json` or `.openpatent/openpatent.json` (supports `$schema` for validation).

- **Model** — set a default with `"model": "provider/model-id"` or choose per session
- **Provider** — local `baseURL`, API keys, and provider-specific options
- **Agents** — override permissions, prompts, and tool access
- **Wiki** — matter wiki under `.openpatent/wiki/`; master wiki in the global config path

Environment variables are supported for provider credentials where applicable.

Full reference: [documentation.md](documentation.md)

---

## Repository layout

```
packages/openpatent/   Core CLI, agents, tools, wiki service
packages/desktop/      Tauri desktop app
packages/app/          Web UI
.openpatent/wiki/      Wiki schema and project-level wiki (when initialized)
```

Built on the agent-first [OpenCode](https://opencode.ai) foundation ([anomalyco/opencode](https://github.com/anomalyco/opencode)), adapted for patent practice.

---

## License

MIT — see [LICENSE](LICENSE).

## Contact

**Tech Tank**  
[openpatent@techtank.com.tr](mailto:openpatent@techtank.com.tr)

# OpenPatent Documentation

> **AI-powered patent office suite for the command line.**
> Built by **Tech Tank** · openpatent@techtank.com.tr

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Installation](#2-installation)
3. [Configuration](#3-configuration)
4. [Getting Started](#4-getting-started)
5. [Agents](#5-agents)
6. [Patent-Specific Tools](#6-patent-specific-tools)
7. [TUI Reference — Commands & Keybinds](#7-tui-reference--commands--keybinds)
8. [Working with Patent Documents](#8-working-with-patent-documents)
9. [Workflow Examples](#9-workflow-examples)
10. [Configuration Reference](#10-configuration-reference)
11. [MCP Server Integration](#11-mcp-server-integration)
12. [Sharing Sessions](#12-sharing-sessions)
13. [Customization](#13-customization)
14. [Troubleshooting](#14-troubleshooting)

---

## 1. Introduction

OpenPatent is an AI-powered patent office suite that runs in your terminal. It enables patent professionals — attorneys, agents, engineers, and paralegals — to handle the full spectrum of patent work from a single, intelligent command-line interface.

OpenPatent is not a simple chatbot. It is an **agentic system**: it reads and writes files, searches patent databases, executes structured legal analysis, and delegates sub-tasks to specialist agents — all autonomously, within a session context it builds and maintains throughout your work.

### What OpenPatent Can Do

| Task Area | Examples |
|-----------|---------|
| **Drafting** | Full patent applications, provisional applications, continuation drafts |
| **Prosecution** | Office action responses, claim amendments, MPEP-based arguments |
| **Consulting** | Patentability opinions, FTO analysis, validity opinions |
| **Prior Art** | Patent database search, claim mapping, landscape analysis |
| **Litigation** | Claim construction, infringement contentions, invalidity arguments |
| **Portfolio** | Docket tracking, maintenance fee reminders, status reports |
| **Strategy** | Claim strategy, competitive intelligence, prosecution planning |

### What Makes OpenPatent Different

- **Patent-native** — every tool, prompt, and agent is calibrated specifically for IP law, not repurposed from a coding assistant
- **MPEP-aware** — the system has structural knowledge of the Manual of Patent Examining Procedure
- **Multi-agent** — complex tasks are broken down and delegated to specialist subagents (prior art search, claim analysis, legal research)
- **Document-oriented** — works directly with your local patent files (`.docx`, `.pdf`, `.txt`, `.md`)
- **Model-agnostic** — plugs into any LLM provider: Anthropic, OpenAI, Google, local Ollama models, and more

---

## 2. Installation

### Quick Install (macOS / Linux)

```bash
curl -fsSL https://openpatent.techtank.com.tr/install | bash
```

### Using Node.js / Bun

```bash
# npm
npm install -g openpatent

# bun
bun install -g openpatent

# pnpm
pnpm install -g openpatent
```

### Using Homebrew (macOS / Linux)

```bash
brew install techtank/tap/openpatent
```

### Windows

For the best experience on Windows, use [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install).

```powershell
# Using Chocolatey
choco install openpatent

# Using Scoop
scoop install openpatent

# Using npm
npm install -g openpatent
```

### Desktop App (Tauri)

A native desktop app is available for macOS, Windows, and Linux via the [Releases page](https://github.com/techtank/openpatent/releases). Download the appropriate installer for your platform.

### From Source

```bash
git clone https://github.com/techtank/openpatent.git
cd openpatent
bun install
bun run dev
```

---

## 3. Configuration

OpenPatent works with any major LLM provider. You must configure at least one before first use.

### Quick Setup via TUI

Launch OpenPatent and run the `/connect` command:

```
/connect
```

Select your provider, enter your API key when prompted, and you're ready.

### Manual Configuration

Create a configuration file at one of these locations:

| Scope | Path |
|-------|------|
| Global (all projects) | `~/.openpatent/openpatent.json` |
| Per-project | `.openpatent/openpatent.json` in project root |

**Minimal configuration example:**

```json
{
  "provider": {
    "anthropic": {
      "api_key": "sk-ant-..."
    }
  },
  "model": {
    "modelId": "anthropic/claude-sonnet-4-5"
  }
}
```

### Supported Providers

OpenPatent works with all major LLM providers:

| Provider | Notes |
|----------|-------|
| **Anthropic** | Recommended — Claude models excel at long legal documents |
| **OpenAI** | GPT-4o, o3 series |
| **Google** | Gemini 2.5 Pro — strong for long-context patent analysis |
| **Amazon Bedrock** | Enterprise deployments |
| **Ollama** | Local, fully private — ideal for confidential matters |
| **OpenRouter** | Route to any model via a single API key |
| **Azure OpenAI** | Enterprise compliance |
| **LM Studio** | Local model hosting |
| Any OpenAI-compatible API | Set a custom base URL |

**Provider-via-environment-variable:**

```bash
ANTHROPIC_API_KEY=sk-ant-... openpatent
OPENAI_API_KEY=sk-...        openpatent
GOOGLE_API_KEY=...           openpatent
OLLAMA_HOST=http://localhost:11434 openpatent
```

> **For confidential patent matters**, we recommend using Ollama with a local model. No data leaves your machine.

---

## 4. Getting Started

### Initialize a Matter

Navigate to the directory where you want to work — this could be a matter folder, a client folder, or just your home directory:

```bash
cd ~/matters/client-xyz/patent-application
openpatent
```

Then initialize OpenPatent for this matter:

```
/init
```

This analyzes the folder and creates an `AGENTS.md` file describing the matter context — the technology area, the client, existing documents, and any relevant prior art already in the folder. Commit this file to your version control system.

### Reference Files in Your Prompts

Use the `@` key to fuzzy-search and attach files from your matter folder:

```
Draft independent claim 1 based on the invention disclosure at @disclosure.pdf
```

```
Review the office action at @OA-2025-03-01.pdf and suggest arguments
```

### Undo and Redo

If OpenPatent drafts something you don't want:

```
/undo
```

This reverts the last change and restores your previous prompt — you can then refine and try again.

To redo:

```
/redo
```

---

## 5. Agents

OpenPatent uses a **multi-agent architecture**. Different agents have different system prompts, tool access, and task focus. You can switch agents at any time using the `Tab` key or the `/agent` command.

### Primary Agents

| Agent | Command | Purpose |
|-------|---------|---------|
| `draft` | `Tab` (default) | Full patent application drafting |
| `prosecute` | `/agent prosecute` | Office action responses, amendments |
| `consult` | `/agent consult` | Read-only analysis and opinions |
| `litigate` | `/agent litigate` | Litigation support and claim analysis |
| `manage` | `/agent manage` | Portfolio and docket management |
| `strategy` | `Tab` (plan mode) | Research, planning, and strategy |

### Specialist Subagents

These agents are invoked automatically by the primary agents when complex sub-tasks arise. You can also invoke them directly:

| Subagent | Role |
|----------|------|
| `prior-art` | Patent database searching and mapping |
| `analyst` | Technical analysis and claim charting |
| `claims-analyst` | Claim scope interpretation and differentiation |
| `legal-research` | MPEP lookups, case law, and precedent |
| `document-writer` | Formal document formatting and output |
| `reviewer` | Quality review of drafts before finalization |

### Switching Between Draft and Strategy Mode

OpenPatent has two primary modes, toggled with `Tab`:

- **Draft mode** — `draft` agent is active; OpenPatent writes documents and makes file changes
- **Strategy mode** — `strategy` agent is active; read-only planning mode, no files are modified

Use Strategy mode to think through an approach before committing to a document. Press `Tab` again to switch back to Draft mode and execute.

**Example workflow:**

1. Press `Tab` → enter Strategy mode
2. Ask: *"What are the strongest claim differentiation arguments against the cited art in this office action?"*
3. Review the strategy analysis
4. Press `Tab` → return to Draft mode
5. Ask: *"OK, go ahead and draft the response based on that strategy"*

### Customizing Agent Behavior

You can customize any agent's instructions in your project-level `AGENTS.md` or in the config:

```json
{
  "agents": {
    "draft": {
      "instructions": "Always draft claims in claim sets of 20. Use 35 USC 112(f) means-plus-function language only when explicitly requested. Prefer method claims over apparatus claims for software inventions."
    }
  }
}
```

---

## 6. Patent-Specific Tools

OpenPatent ships with a set of tools specifically designed for patent work. These are invoked automatically by agents as needed, and can also be called via the `/tool` command.

### `patent-search`

Searches patent databases (USPTO, EPO, Google Patents) for prior art.

```
Search for prior art related to the transformer attention mechanism claims in @claims-draft.txt
```

**Parameters:**
- `query` — natural language or keyword search string
- `database` — `"uspto"`, `"epo"`, `"wipo"`, or `"all"` (default: `"all"`)
- `date_range` — e.g. `"2010-2024"`
- `classification` — CPC/IPC class codes, e.g. `"G06N3/04"`

### `claim-parser`

Parses claim text into structured form — preamble, transition, body elements, and dependencies.

```
Parse and analyze the claim structure in @claims-draft.txt — identify any issues with antecedent basis
```

**Output:** Structured JSON representation of each claim, with element mapping and dependency tree.

### `mpep-lookup`

Looks up sections of the Manual of Patent Examining Procedure.

```
What does MPEP 2111 say about claim construction?
```

```
Look up the requirements for a continuation-in-part under MPEP 201.11
```

### `docket-query`

Queries patent office docket systems for case status, deadlines, and office actions.

```
What is the status of application 17/123,456?
```

```
List all applications with deadlines in the next 30 days for client Acme Corp
```

### `document-template`

Generates patent documents from structured templates.

- Utility patent application (US provisional and non-provisional)
- PCT application (PCT/RO/101)
- Office action response
- Appeal brief
- Declaration of inventorship (ADS)
- Assignment agreement

```
Generate a provisional patent application template for a medical device invention
```

### `compliance-check`

Validates documents against USPTO, EPO, or WIPO formal requirements.

```
Check this application for formal compliance with USPTO requirements before filing
```

**Checks performed:**
- Claims count (≤20 total, ≤3 independent for small entity)
- Claim dependency correctness
- Abstract length (≤150 words)
- Drawing figure references
- Specification completeness (written description, enablement)
- 35 USC 112 format issues

### `citation-format`

Formats patent and non-patent literature citations to standard styles.

```
Format these references for an IDS submission: [paste list]
```

**Supported formats:** USPTO IDS (SB/08), EPO Forms, IEEE, APA, MPEP citation style.

---

## 7. TUI Reference — Commands & Keybinds

### Slash Commands

| Command | Description |
|---------|-------------|
| `/init` | Initialize OpenPatent for the current matter folder |
| `/connect` | Connect an LLM provider |
| `/agent <name>` | Switch to a named agent |
| `/tool <name>` | Invoke a specific tool |
| `/share` | Share the current session as a link |
| `/undo` | Undo the last change |
| `/redo` | Redo the last undone change |
| `/clear` | Clear the conversation history |
| `/compact` | Summarize conversation to reduce context usage |
| `/help` | Show all available commands |
| `/quit` | Exit OpenPatent |

### Keybinds

| Key | Action |
|-----|--------|
| `Tab` | Switch between Draft mode and Strategy mode |
| `@` | Open file picker to attach a file to the prompt |
| `Ctrl+C` | Interrupt the current operation |
| `Ctrl+L` | Clear session display |
| `Ctrl+Z` | Undo last change |
| `Ctrl+Y` | Redo last change |
| `↑` / `↓` | Navigate conversation history |
| `Esc` | Cancel current input |
| `Enter` | Submit prompt |
| `Shift+Enter` | Add newline without submitting |

### Keyboard Shortcuts in Strategy Mode

| Key | Action |
|-----|--------|
| `Tab` | Return to Draft mode |
| `Ctrl+C` | Stop current analysis |

---

## 8. Working with Patent Documents

### Referencing Files

OpenPatent can read any file in your matter folder. Use `@` to attach them:

```
Review @OA-2025-02-15.pdf and draft a response
```

```
Compare the claims in @US10123456.pdf with our draft at @draft-claims.txt and identify overlapping scope
```

**Supported formats:** `.pdf`, `.docx`, `.txt`, `.md`, `.json`, `.xml`

For PDFs, OpenPatent extracts text automatically. For scanned documents, use an OCR tool first to produce a text version.

### Organizing a Matter Folder

We recommend this folder structure for each patent matter:

```
matter-client-invention/
  AGENTS.md              ← OpenPatent matter context (auto-generated by /init)
  disclosure/
    invention-disclosure.pdf
    drawings/
  prosecution/
    application-as-filed.docx
    OA-2024-05-01.pdf
    response-2024-07-01.docx
  prior-art/
    search-results.md
    cited-patents/
  claims/
    claims-v1.txt
    claims-v2.txt
  notes.md
```

### AGENTS.md

The `AGENTS.md` file is the primary context document. OpenPatent reads it at the start of every session. Keep it up to date with:

- Invention summary
- Technology area and CPC classification
- Claims strategy notes
- Prosecution history summary
- Key prior art references
- Client-specific instructions (claim formatting preferences, claim length, style)

**Example AGENTS.md:**

```markdown
# Matter: Acme Corp — Smart Sensor Array (US App. 17/123,456)

## Technology Area
IoT sensor fusion, machine learning, embedded systems.
CPC: G01D21/00, H04L67/12, G06N3/08

## Invention Summary
A sensor array system that uses on-device ML inference to fuse heterogeneous
sensor signals and produce calibrated measurements without cloud connectivity.

## Claim Strategy
- Emphasize the on-device inference and the absence of cloud dependency
- Independent claim 1 should cover the method; claim 12 the apparatus
- Avoid means-plus-function language per client preference

## Current Status
Office Action issued 2025-02-15. Primary rejections: 102 (Chen, US10789123)
and 103 (Chen in view of Smith, US9876543). Response due 2025-05-15.

## Client Preferences
- Claims: 20 total, 3 independent
- Abstract: ≤100 words
- Drawings: Professional engineering style, not schematic
```

---

## 9. Workflow Examples

### Example 1: Drafting a Utility Patent Application

```
1. Start Strategy mode (Tab)

   Draft a strategy for a patent application covering an AI-powered
   ECG monitoring device that detects arrhythmias without requiring
   a cloud connection. The primary innovation is the edge-inference
   algorithm. @disclosure.pdf

2. Review strategy, then switch to Draft mode (Tab)

   OK, that approach looks good. Draft the full application — all
   sections including specification, claims (20 claims), abstract,
   and brief description of drawings.

3. Refine claims

   The independent claim is too broad — let's add a limitation
   requiring that the model be trained on >100,000 patient records.
   Also, reformulate claim 5 as a method claim.

4. Run compliance check

   /tool compliance-check
```

### Example 2: Responding to a 102 Office Action

```
1. Attach the office action

   @OA-2025-02-15.pdf Review this office action and summarize
   each rejection.

2. Switch to Strategy mode (Tab) for analysis

   For the 102 rejection over Chen (US10789123), what
   distinguishing features do our claims have? Also check
   whether Chen actually discloses element [c] of claim 1.

3. Switch to Draft mode (Tab) and execute

   Draft the response. For the 102 rejection, argue that Chen
   does not disclose [c] as I noted. For the 103, amend claim 1
   to add the limitation we discussed and argue non-obviousness
   based on the unexpected result shown in @experimental-data.pdf.
```

### Example 3: Prior Art Search

```
/agent prior-art

Search for prior art in the field of quantum key distribution
over free-space optical links. Focus on systems using adaptive
optics for beam stabilization. Date range: 2015-2025.
Report back with the top 10 most relevant references.
```

### Example 4: FTO Analysis

```
/agent consult

I need a freedom-to-operate analysis for our product described
in @product-spec.pdf. Key competitor patents to check: @US10456789.pdf,
@US11234567.pdf, @EP3456789.pdf.

For each patent, assess whether our product falls within the scope
of the independent claims. Note expired claims separately.
```

### Example 5: Portfolio Management

```
/agent manage

List all matters in this folder with deadlines in the next 60 days.
Flag any with less than 30 days remaining as urgent. Output a table
sorted by deadline ascending.
```

---

## 10. Configuration Reference

The configuration file is a JSON file located at `~/.openpatent/openpatent.json` (global) or `.openpatent/openpatent.json` (per-project).

### Full Config Schema

```json
{
  "model": {
    "modelId": "anthropic/claude-sonnet-4-5",
    "temperature": 0.3,
    "maxTokens": 16000
  },

  "provider": {
    "anthropic": { "api_key": "sk-ant-..." },
    "openai":    { "api_key": "sk-..."},
    "ollama":    { "host": "http://localhost:11434" }
  },

  "agents": {
    "default": "draft",
    "draft": {
      "model": { "modelId": "anthropic/claude-opus-4-5" },
      "instructions": "Always draft claims in dependent claim sets of 20..."
    },
    "consult": {
      "model": { "modelId": "google/gemini-2.5-pro" },
      "instructions": "You are operating in read-only consulting mode. Do not create or modify files."
    }
  },

  "tools": {
    "patent-search": {
      "default_database": "all",
      "max_results": 20
    },
    "compliance-check": {
      "jurisdiction": "USPTO"
    }
  },

  "tui": {
    "theme": "dark",
    "font": "mono"
  },

  "keybinds": {
    "submit": "enter",
    "newline": "shift+enter",
    "mode_switch": "tab"
  },

  "sharing": {
    "enabled": false
  },

  "autoupdate": true,

  "permissions": {
    "allow_file_writes": true,
    "allow_external_requests": true
  },

  "compaction": {
    "enabled": true,
    "threshold_tokens": 80000
  },

  "mcp": {
    "servers": {
      "patent-db": {
        "type": "stdio",
        "command": "openpatent-mcp-server",
        "args": ["--database", "uspto"]
      }
    }
  }
}
```

### Key Config Options

#### `model`
Sets the default model for all agents. You can override per-agent.

- `modelId` — format: `"provider/model-name"`, e.g. `"anthropic/claude-opus-4-5"`
- `temperature` — `0.0`–`1.0`. Lower = more deterministic (recommended: `0.2`–`0.4` for legal drafting)
- `maxTokens` — max output tokens per response

#### `agents.default`
Which agent starts when you launch OpenPatent. Defaults to `"draft"`.

#### `permissions`
- `allow_file_writes` — if `false`, OpenPatent will not write any files (useful for consult mode)
- `allow_external_requests` — if `false`, disables patent database searches and external tool calls

#### `compaction`
When conversation context exceeds `threshold_tokens`, OpenPatent summarizes the conversation to stay within the model's context window. The summary is retained and the original messages are removed.

#### `sharing`
When `enabled: true`, you can use `/share` to generate a public link to a conversation.

---

## 11. MCP Server Integration

OpenPatent supports the **Model Context Protocol (MCP)** for connecting to external data sources and tools.

### What You Can Connect

- **USPTO full-text patent database** — real-time patent search and retrieval
- **EPO Open Patent Services** — European patent data
- **Docketing systems** — connect to your firm's docketing software
- **Prior art databases** — Derwent, PatBase, Questel
- **Document management** — NetDocs, iManage, SharePoint

### Configuring an MCP Server

```json
{
  "mcp": {
    "servers": {
      "my-patent-db": {
        "type": "stdio",
        "command": "/path/to/mcp-server",
        "args": ["--api-key", "YOUR_KEY"]
      },
      "my-docket": {
        "type": "sse",
        "url": "https://your-docket-system.com/mcp"
      }
    }
  }
}
```

### Managing MCP Servers from the CLI

```bash
# List configured servers
openpatent mcp list

# Add a server
openpatent mcp add my-server --command /path/to/server

# Remove a server
openpatent mcp remove my-server

# Test a server connection
openpatent mcp test my-server
```

---

## 12. Sharing Sessions

Patent sessions can be shared with colleagues for review.

```
/share
```

This generates a link to the current session and copies it to your clipboard.

> **Privacy note:** Conversations are **not shared by default**. Sharing must be explicitly enabled in the config (`"sharing": { "enabled": true }`) and then triggered with `/share` in each session you want to share.

> **Confidentiality warning:** Before sharing any session, ensure it does not contain confidential client information that should not be transmitted externally. For maximum confidentiality, disable sharing entirely and use the desktop app with a local Ollama model.

---

## 13. Customization

### Themes

```json
{
  "tui": {
    "theme": "dark"
  }
}
```

Available themes: `dark`, `light`, `monokai`, `solarized`, `one-dark`, `dracula`.

### Custom Keybinds

```json
{
  "keybinds": {
    "submit": "enter",
    "newline": "shift+enter",
    "mode_switch": "tab",
    "undo": "ctrl+z",
    "redo": "ctrl+y"
  }
}
```

### Custom Commands

You can define your own slash commands that expand to common prompts:

```json
{
  "commands": {
    "oa-summary": "Summarize the rejections in the attached office action and list the response deadline.",
    "check-claims": "Parse and audit the claims in the attached document: check antecedent basis, dependency correctness, and 112(f) issues.",
    "boilerplate": "Generate a boilerplate specification section for the attached claims."
  }
}
```

Then use them in the TUI:

```
/oa-summary @OA-2025-03-01.pdf
```

### Formatters

Configure auto-formatting when OpenPatent saves documents:

```json
{
  "formatters": {
    "docx": "pandoc {file}",
    "md": "prettier --write {file}"
  }
}
```

### System-Level Prompt Instructions

Add permanent instructions that apply to every session:

```json
{
  "instructions": [
    "Always cite the MPEP section when making a legal argument.",
    "Use plain language in client-facing documents; use technical language in examiner-facing documents.",
    "When drafting claims, always number them and include a means for claims section if apparatus claims are present."
  ]
}
```

---

## 14. Troubleshooting

### OpenPatent is not responding

- Check your API key is valid: run `/connect` to reconnect
- Check your network connection (required for non-local providers)
- For `ollama` provider, ensure the Ollama daemon is running: `ollama serve`

### Context limit reached

If you see a context limit error, run `/compact` to summarize and reduce the conversation length. You can also start a fresh session with `/clear`.

### PDF text extraction is poor

For scanned PDFs, extract text with an OCR tool before attaching:

```bash
# Using tesseract (macOS: brew install tesseract)
tesseract OA-2025-03-01.pdf OA-2025-03-01 pdf
```

Then attach `@OA-2025-03-01.pdf` in your prompt.

### Compliance check gives false positives

The compliance checker uses heuristic rules. It may flag valid claim language as issues. Always review its output manually; treat it as a checklist aid, not an automated filing system.

### Agent keeps switching back to `draft`

If an agent switch with `/agent` doesn't persist, check whether your config has `"default": "draft"` locked. Remove the `default` key or change it to your preferred agent.

### Getting Help

- **Documentation:** https://openpatent.techtank.com.tr/docs
- **Issues:** https://github.com/techtank/openpatent/issues
- **Email:** openpatent@techtank.com.tr

---

*OpenPatent is built by **Tech Tank** and released under the MIT License.*
*© 2026 Tech Tank. All rights reserved.*

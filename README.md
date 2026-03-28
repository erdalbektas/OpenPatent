# OpenPatent

**AI-powered patent office suite for the command line.**

OpenPatent is an intelligent, terminal-based assistant designed for patent professionals. It leverages large language models to help with patent drafting, prosecution, consulting, litigation support, portfolio management, and strategic planning — all from the comfort of your CLI.

> Built by **Tech Tank** · Contact: openpatent@techtank.com.tr

---

## Features

- **Patent Drafting** — Draft complete patent applications including claims, specifications, abstracts, and drawing descriptions
- **Prosecution** — Respond to office actions, draft amendments, and construct arguments
- **Consulting** — Patentability opinions, freedom-to-operate analysis, landscape analysis, and validity opinions
- **Litigation Support** — Claim construction, infringement analysis, and invalidity contentions
- **Portfolio Management** — Docket tracking, deadline management, and status reports
- **Strategic Planning** — Prior art landscape analysis and claim strategy planning

## Agent Architecture

OpenPatent ships with 6 primary workflow agents and 6 specialist subagents:

| Agent       | Purpose                                   |
| ----------- | ----------------------------------------- |
| `draft`     | Default agent. Drafts patent applications |
| `prosecute` | Office action responses and amendments    |
| `consult`   | Read-only consulting and opinions         |
| `litigate`  | Litigation support and analysis           |
| `manage`    | Portfolio and docket management           |
| `strategy`  | Research and planning mode                |

**Subagents** (invoked via task delegation): `prior-art`, `analyst`, `claims-analyst`, `legal-research`, `document-writer`, `reviewer`

## Patent-Specific Tools

| Tool                | Description                    |
| ------------------- | ------------------------------ |
| `patent-search`     | Search patent databases        |
| `claim-parser`      | Parse claim structure          |
| `mpep-lookup`       | Look up MPEP sections          |
| `docket-query`      | Query patent docket status     |
| `document-template` | Generate from patent templates |
| `compliance-check`  | Validate PTO requirements      |
| `citation-format`   | Format patent citations        |

## Getting Started

### Prerequisites

- [Bun](https://bun.sh/) runtime
- An API key for a supported LLM provider (OpenAI, Anthropic, Google, etc.)

### Installation

```bash
# Clone the repository
git clone https://github.com/techtank/openpatent.git
cd openpatent

# Install dependencies
bun install

# Run in development mode
bun run dev
```

### Configuration

Create a `.openpatent/openpatent.json` file in your project or home directory:

```json
{
  "provider": {
    "anthropic": {
      "api_key": "YOUR_API_KEY"
    }
  }
}
```

Alternatively, set environment variables:

```bash
export OPENPATENT_API_KEY="your-api-key"
```

### Usage

```bash
# Start OpenPatent
openpatent

# Start in a specific agent mode
openpatent --agent draft
openpatent --agent prosecute
openpatent --agent consult
```

## Project Structure

```
packages/
  openpatent/          # Core application
    src/
      agent/         # Agent definitions and prompts
      tool/          # Patent-specific tools
      session/       # Session management and system prompts
      config/        # Configuration handling
      cli/           # Command-line interface
```

## Development

```bash
# Run tests
bun test

# Build for production
bun run build

# Run as desktop app (Tauri)
bun run dev:desktop
```

## License

MIT

## Contact

**Tech Tank**
Email: openpatent@techtank.com.tr

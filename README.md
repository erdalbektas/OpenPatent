# OpenPatent

**Local, open-source AI for patent drafting** — built on [OpenCode 2](https://opencode.ai).

OpenPatent adds a matter workspace, specialized agents, and deterministic patent tools on top of OpenCode. Run models locally (Ollama, LM Studio, etc.) or with your own cloud providers. No separate Django server is required.

## Built on OpenCode

This repository tracks [anomalyco/opencode](https://github.com/anomalyco/opencode) `dev` (see [UPSTREAM.md](UPSTREAM.md)). Core agent runtime, sessions, and the desktop/web clients come from upstream; patent-specific code lives in `packages/patent*` and `packages/openpatent`.

## Quick start

```bash
bun install
bun run packages/openpatent/bin/openpatent.ts init ./my-matter --title "Widget controller"
cd my-matter
bun run --cwd ../.. packages/openpatent/bin/openpatent.ts
```

Configure providers in `opencode.jsonc` (copied into the matter by `init`). Set `PATENTSVIEW_API_KEY` for USPTO PatentsView prior-art search.

## Agents

| Agent | Role |
| --- | --- |
| `counsel` | Primary workflow orchestrator |
| `interrogator` | Disclosure gap analysis |
| `searcher` | Prior art search |
| `drafter` | Claims and specification |
| `examiner` | Pre-filing examination memo |
| `illustrator` | Figures and reference numerals |
| `prosecutor` | Office action responses |

Enable the plugin in `opencode.jsonc`:

```json
{
  "plugins": ["@openpatent/plugin"],
  "default_agent": "counsel"
}
```

## Matter layout

```text
openpatent.json
disclosure/invention.md
claims/claims.md
specification/spec.md
figures/numerals.json
references/index.json
glossary.json
prosecution/
status.json
```

## License

MIT. OpenPatent includes code from OpenCode (MIT). See [LICENSE](LICENSE).

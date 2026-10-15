# OpenPatent branding on OpenCode

Upstream OpenCode packages keep their original names (`@opencode/*`, `opencode` binary internals). OpenPatent branding is limited to the following intentional touchpoints:

| Area | Path | Change |
| --- | --- | --- |
| Product docs | [README.md](README.md) | OpenPatent positioning, MIT + OpenCode attribution |
| Upstream tracking | [UPSTREAM.md](UPSTREAM.md) | Pinned OpenCode revision |
| User command | [packages/openpatent/bin/openpatent.ts](packages/openpatent/bin/openpatent.ts) | `openpatent` CLI wrapper around `packages/cli` |
| Patent domain | [packages/patent/](packages/patent/) | Matter model, tools, tests |
| Patent plugin | [packages/patent-plugin/](packages/patent-plugin/) | Agents and OpenCode v2 plugin |
| Matter UI (optional) | [packages/app/src/matter/](packages/app/src/matter/) | File-backed matter summary route |

Do not rename `packages/core`, `packages/cli`, or other upstream directories. Merge conflicts with `anomalyco/opencode` `dev` should be resolved in the table above plus this file.

Future desktop or installer branding (window title, icons, about dialog) should be listed here before landing.

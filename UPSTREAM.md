# Upstream OpenCode

OpenPatent is built on [OpenCode](https://github.com/anomalyco/opencode). Product-specific code lives under `packages/patent*`, `packages/openpatent`, and the files listed in [BRAND.md](BRAND.md).

## Pinned revision

| Field | Value |
| --- | --- |
| Remote | `https://github.com/anomalyco/opencode.git` |
| Branch | `dev` |
| Commit | `4397ee44d038a5f17bf6ac161431673d93e563b5` |
| Version (package.json) | `2.0.29` |
| Imported | 2026-10-15 |

## Merge upstream

```bash
git remote add upstream https://github.com/anomalyco/opencode.git  # once
git fetch upstream dev
git merge upstream/dev
```

Resolve conflicts only in `BRAND.md`, product `README.md`, `UPSTREAM.md`, and `packages/patent*`, `packages/openpatent`, plus intentional brand patches under upstream packages documented in `BRAND.md`.

After merging, update the pinned commit table in this file.

# Contributing to OpenPatent

We want to make it easy for you to contribute to OpenPatent. Here are the most common type of changes that get merged:

- Bug fixes
- Additional patent agents
- Improvements to agent performance
- Support for new LLM providers
- Fixes for environment-specific quirks
- Missing standard behavior
- Documentation improvements

However, any UI or core product feature must go through a design review with the core team before implementation.

If you are unsure if a PR would be accepted, feel free to ask a maintainer or look for issues with any of the following labels:

- [`help wanted`](https://github.com/openpatent/openpatent/issues?q=is%3Aissue%20state%3Aopen%20label%3Ahelp-wanted)
- [`good first issue`](https://github.com/openpatent/openpatent/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
- [`bug`](https://github.com/openpatent/openpatent/issues?q=is%3Aissue%20state%3Aopen%20label%3Abug)
- [`perf`](https://github.com/openpatent/openpatent/issues?q=is%3Aopen%20is%3Aissue%20label%3A%22perf%22)

> [!NOTE]
> PRs that ignore these guardrails will likely be closed.

Want to take on an issue? Leave a comment and a maintainer may assign it to you unless it is something we are already working on.

## Developing OpenPatent

- Requirements: Bun 1.3+
- Install dependencies and start the dev server from the repo root:

  ```bash
  bun install
  bun dev
  ```

### Running against a different directory

By default, `bun dev` runs OpenPatent in the `packages/opencode` directory. To run it against a different directory or repository:

```bash
bun dev <directory>
```

To run OpenPatent in the root of the openpatent repo itself:

```bash
bun dev .
```

### Project Structure

```
openpatent/
├── openpatent_django/        # Django server for premium agents
│   └── apps/patent/        # Patent agents and models
├── packages/
│   ├── desktop/            # Tauri desktop application
│   ├── app/                # SolidJS core UI
│   ├── openpatent/         # CLI tool (patent workflow)
│   └── ui/                 # UI components
├── docs/                   # Documentation
└── patent_suite/           # Standalone patent tools
```

### Testing

```bash
# Django tests
cd openpatent_django
python manage.py test apps.patent.tests.test_agents

# Frontend tests
cd packages/desktop
bun test
```

## Code Style

OpenPatent follows the style guide in `STYLE_GUIDE.md`. Key points:

- Use Bun APIs where possible
- Avoid try/catch when possible
- Avoid else statements
- Prefer single word variables where possible
- No comments unless explicitly requested

## Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Getting Help

- Discord: https://openpatent.ai/discord
- GitHub Issues: https://github.com/openpatent/openpatent/issues

# Dev Guardrails

An opinionated, continuously curated list of tools for **enforcing** software development standards.

Dev Guardrails is not an Awesome List. It does not list every linter for every language. For each job it recommends one tool (rarely two), says why, and says where the tool stops working.

## Principles

- **Opinionated.** One recommended tool per job. Several only when the jobs or the environments really differ.
- **Curated.** Every tool is checked against the [selection criteria](CONTRIBUTING.md#selection-criteria) before it is listed, and again on a schedule.
- **Coverage over quantity.** A tool that replaces three narrow checks beats three narrow tools.
- **Enforcement over advice.** A tool must fail a build (non-zero exit code) when a standard is violated. Reports that nobody reads do not count.
- **Agent-friendly.** Non-interactive, machine-readable output, clear diagnostics, and autofix where it is safe. AI coding agents are first-class users of these tools.
- **Honest about gaps.** A category with no verified recommendation stays empty rather than getting an outdated one.

This is **not a universal stack**. Do not install everything here. Pick the entries that match your project.

## Recommendations

Each entry is backed by a record in [`tools.json`](tools.json): date of the last review, sources, rationale and limitations. Review dates are 2026-10-23 unless noted.

### GitHub Actions

- **[jactionlint](https://github.com/jdx/jactionlint)**: lints workflows, composite actions and `dependabot.yml` for correctness, security and policy in one binary. It is a fork of actionlint whose security rules follow the audits of zizmor, so you do not need `actionlint` or `zizmor` next to it by default. `--fix` repairs what has a mechanical fix; with `--online` it also pins tags to commit SHAs. *Limits:* created in October 2026 and run by one maintainer; parity with zizmor is self-reported. If you need an established second implementation, offline archived-action detection, pre-commit config audits or an LSP, add [zizmor](https://github.com/zizmorcore/zizmor). [Details](research/github-actions.md).

### Python

- **[Ruff](https://github.com/astral-sh/ruff)**: linter and formatter that replaces Flake8, isort, pyupgrade and Black. *Limits:* no type checking, no custom-rule plugins.
- **[deptry](https://github.com/osprey-oss/deptry)**: unused, missing and transitive dependencies. *Limits:* static analysis misses dynamic imports.

### Go

- **[golangci-lint](https://github.com/golangci/golangci-lint)**: one runner for the Go linters and the formatter, with `golangci-lint custom` for your own analyzers. *Limits:* choose linters deliberately; GPL-3.0.

### Rust

- **[Clippy](https://github.com/rust-lang/rust-clippy)**: the official linter; run `cargo clippy -- -D warnings`. *Limits:* tied to the toolchain version.

### Ruby

- **[RuboCop](https://github.com/rubocop/rubocop)**: linter and formatter with autocorrect and custom cops. *Limits:* slower than native-code linters.

### Shell

- **[ShellCheck](https://github.com/koalaman/shellcheck)**: bugs and portability problems in `sh`, `bash`, `dash` and `ksh`. *Limits:* a stable-tool exception, last release in August 2025 with ongoing commits; no zsh. jactionlint already runs it on workflow `run:` steps.

### JavaScript and TypeScript

- **[Knip](https://github.com/webpro-nl/knip)**: unused files, exports and dependencies. *Limits:* monorepos need configuration; never run `--fix` unattended.

### Custom rules

- **[ast-grep](https://github.com/ast-grep/ast-grep)**: project-specific syntax rules as YAML, with tests for the rules themselves (`ast-grep test`). *Limits:* syntax only, no data-flow analysis.

### Git conventions

- **[commitlint](https://github.com/conventional-changelog/commitlint)**: Conventional Commits for a message, a hook or a CI range. *Limits:* needs Node; checks format, not accuracy.

### Documentation

- **[markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2)**: Markdown style and structure. *Limits:* no prose or spelling checks.
- **[lychee](https://github.com/lycheeverse/lychee)**: broken links. *Limits:* network flakiness; give it a GitHub token and a cache.
- **[typos](https://github.com/crate-ci/typos)**: low-noise spell checking of source code and docs. *Limits:* finds only known misspellings.

## Under review

These categories matter but have **no recommendation yet**: the candidates have not been compared properly. Names below are research leads, not endorsements.

| Category | Candidates | Why it is still open |
|---|---|---|
| JavaScript / TypeScript linting and formatting | ESLint, Biome, Oxlint with oxfmt | Three active tools with different coverage and plugin support. |
| Secrets | Gitleaks, TruffleHog | Gitleaks' last release is March 2026; maintenance needs a closer look. TruffleHog is AGPL-3.0. |
| Vulnerabilities and images | OSV-Scanner, Trivy | Trivy's GitHub Action and a release were compromised in March 2026 ([advisory](https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23)); it has since been fixed, but the overlap with OSV-Scanner and others is not yet decided. |
| Custom rules with data-flow | Semgrep, Opengrep | Opengrep is a community fork after Semgrep's licensing changes. |
| Git hooks | hk, prek, pre-commit, Lefthook | Runner choice depends on the toolchain. |
| Docker, Terraform, Kubernetes | Hadolint, TFLint, Checkov, kube-linter, Kubeconform | Overlap with Trivy and Checkov first. |
| API contracts | vacuum, Spectral, Redocly CLI, Buf | Several OpenAPI linters with overlapping rules. |
| SQL and migrations | squawk, SQLFluff, Atlas | Migration safety and SQL style are different jobs. |
| Architecture | dependency-cruiser, ArchUnit, import-linter | One per ecosystem; needs an individual review each. |
| Config files | yamllint, check-jsonschema | Possible overlap with editor and schema tooling. |
| Supply chain and licenses | Scorecard, Syft, ScanCode Toolkit | Mostly reporting tools; needs an enforcement angle. |

## How this list is kept current

- [`tools.json`](tools.json) records the last review date, sources, rationale and limitations of each tool.
- A [weekly workflow](.github/workflows/freshness.yml) flags archived repositories, old pushes and stale releases. It is a signal, not a verdict: a quiet repository can be a finished one, and a busy one can be the wrong choice.
- Replacements need a written comparison. See [CONTRIBUTING.md](CONTRIBUTING.md).
- Tools we looked at and did not take are in [docs/not-adopted.md](docs/not-adopted.md).
- Reusable setup patterns (hooks, CI, generated-code gates) are in [docs/patterns.md](docs/patterns.md).

## License

[CC0 1.0](LICENSE): public domain. Take what is useful.

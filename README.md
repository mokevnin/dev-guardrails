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

The entries below are **generated from [`tools.json`](tools.json)** (`npm run readme`), which records the review date, sources, rationale and limitations of each tool. Every entry was first checked on 2026-10-23: that is one sweep, not independent reviews. Where a claim was tested by running the tool, the entry says so; otherwise it rests on documentation and repository activity.

<!-- tools:start -->

### GitHub Actions

- **[jactionlint](https://github.com/jdx/jactionlint)**: lints workflows, composite actions and `dependabot.yml` for correctness, security and policy in one binary. It is a fork of actionlint whose security rules follow the audits of zizmor, so you do not need `actionlint` or `zizmor` next to it by default. `--fix` repairs what has a mechanical fix; with `--online` it also pins tags to commit SHAs. *Limits:* created in October 2026 and run by one maintainer; parity with zizmor is self-reported. If you need an established second implementation, offline archived-action detection, pre-commit config audits or an LSP, add [zizmor](https://github.com/zizmorcore/zizmor). [Details](research/github-actions.md).

### JavaScript and TypeScript

- **[Knip](https://github.com/webpro-nl/knip)**: unused files, exports and dependencies. *Limits:* monorepos need configuration; never run `--fix` unattended.
- **[ESLint](https://github.com/eslint/eslint)**: linter for JavaScript, TypeScript, JSX, Vue, Svelte and Angular with `--fix`, JSON/SARIF-capable formatters, `--max-warnings 0` and stable custom rules; use typescript-eslint for type-aware rules. Chosen because no faster tool covers framework templates and custom rules as completely. *Limits:* slow on large repos; typescript-eslint does not support TypeScript 7 yet, so type-aware linting needs TypeScript 6.x. For speed-first repos without template linting see [Oxlint](https://github.com/oxc-project/oxc) (exits 0 on warnings unless `--deny-warnings`). [Details](research/stack-javascript.md).
- **[Prettier](https://github.com/prettier/prettier)**: formatting for JS, TS, CSS, Markdown, JSON, YAML and more; `prettier --check` fails CI. Chosen as the reference output with the widest language coverage. *Limits:* slower than oxfmt and Biome; oxfmt is 0.x and kept as a candidate to re-review. [Details](research/stack-javascript.md).
- **[TypeScript](https://github.com/microsoft/TypeScript)**: `tsc --noEmit` with `strict`; version 7 is the native, much faster compiler. *Limits:* the TypeScript 7 compiler API is not ready, so tools that import `typescript` may need TypeScript 6 beside it. `microsoft/typescript-go` is archived because it was merged, not abandoned. [Details](research/stack-javascript.md).
- **[dependency-cruiser](https://github.com/sverweij/dependency-cruiser)**: import-graph rules (forbidden paths, cycles, orphans, dev-deps in production code) with non-zero exit and JSON output; `--ignore-known` baselines legacy violations. Chosen over eslint-plugin-boundaries because it does not depend on the lint stack. *Limits:* static analysis misses dynamic imports; no autofix. [Details](research/stack-javascript.md).

### Python

- **[Ruff](https://github.com/astral-sh/ruff)**: linter and formatter that replaces Flake8, isort, pyupgrade and Black. *Limits:* no type checking, no custom-rule plugins. The `S` rules replace Bandit, `D` replaces pydocstyle (archived) and `C901` replaces xenon and radon; pair with vulture for dead code across modules.
- **[deptry](https://github.com/osprey-oss/deptry)**: unused, missing and transitive dependencies. *Limits:* static analysis misses dynamic imports.
- **[vulture](https://github.com/jendrikseipp/vulture)**: unused functions, classes and variables across modules, which Ruff cannot see. *Limits:* heuristic; needs a whitelist for framework entry points. [Details](research/stack-python-ruby-php.md).
- **[import-linter](https://github.com/seddonym/import-linter)**: import contracts (layers, forbidden, independence, protected) that fail CI. *Limits:* checks imports only; [tach](https://github.com/tach-org/tach) is the alternative for public-interface rules. [Details](research/stack-python-ruby-php.md).

### Go

- **[golangci-lint](https://github.com/golangci/golangci-lint)**: one runner for the Go linters and the formatter, with `golangci-lint custom` for your own analyzers. *Limits:* choose linters deliberately; GPL-3.0.
- **[govulncheck](https://github.com/golang/vuln)**: reports known vulnerabilities in the Go modules and standard library you actually call, with call stacks, from the official Go vulnerability database. *Limits:* with `-json` and `-format sarif` it exits 0 whatever it finds, so gate on the text output; blind to calls through `reflect`; the GitHub repo is a mirror of `golang.org/x/vuln`. For repos in several languages see the open Vulnerabilities decision. [Details](research/stack-go-rust-jvm-dotnet.md).
- **[go-test-coverage](https://github.com/vladopajic/go-test-coverage)**: fails the build when total, per-package or per-file test coverage drops below a threshold, locally with no service, and can compare against the base branch. *Limits:* GPL-3.0, one main maintainer; measures coverage, not test quality. [Details](research/stack-go-rust-jvm-dotnet.md).

### Rust

- **[Clippy](https://github.com/rust-lang/rust-clippy)**: the official linter; run `cargo clippy -- -D warnings`. *Limits:* tied to the toolchain version.
- **[rustfmt](https://github.com/rust-lang/rustfmt)**: the official formatter; run `cargo fmt --check` in CI. *Limits:* versioned with the Rust toolchain, not through GitHub releases; style options are few by design. [Details](research/stack-go-rust-jvm-dotnet.md).
- **[cargo-deny](https://github.com/EmbarkStudios/cargo-deny)**: one policy file for RustSec advisories, licences, banned or duplicate crates and allowed registries; non-zero exit on violation. It replaces `cargo-audit` for the advisory check. *Limits:* checks metadata only, not dependency source; needs a maintained `deny.toml`. [Details](research/stack-go-rust-jvm-dotnet.md).
- **[cargo-semver-checks](https://github.com/obi1kenobi/cargo-semver-checks)**: for libraries you publish, fails on API changes that break semver compared with the last release. *Limits:* libraries only; relies on unstable rustdoc JSON, so a new Rust release can lag. [Details](research/stack-go-rust-jvm-dotnet.md).

### Ruby

- **[RuboCop](https://github.com/rubocop/rubocop)**: linter and formatter with autocorrect and custom cops. *Limits:* slower than native-code linters. Add the `rubocop-rails`, `rubocop-rspec` (or `rubocop-minitest`) and `rubocop-performance` plugins as needed; Standard is a wrapper and not needed.

### PHP

- **[PHPStan](https://github.com/phpstan/phpstan)**: static analysis with levels and a baseline; the widest extension set (Larastan, Symfony, strict rules, dead-code detection). Chosen over Psalm (one active maintainer, 7.0 still in RC). *Limits:* no SARIF; use Larastan for Laravel. [Details](research/stack-python-ruby-php.md).
- **[PHP-CS-Fixer](https://github.com/PHP-CS-Fixer/PHP-CS-Fixer)**: code style check and fix, parallel by default, custom fixers. *Limits:* Laravel projects should use [Pint](https://github.com/laravel/pint), the same engine with Laravel defaults; run one, not both. [Details](research/stack-python-ruby-php.md).
- **[Deptrac](https://github.com/deptrac/deptrac)**: layer dependency rules. *Limits:* use the `deptrac/deptrac` repository (the old `qossmic/deptrac` is archived); static dependencies only. [Details](research/stack-python-ruby-php.md).

### Java

- **[Error Prone](https://github.com/google/error-prone)**: bug patterns checked by the Java compiler on every build; raise a check to `ERROR` to fail the build. With [NullAway](https://github.com/uber/NullAway) as a plugin it also enforces null safety from `@Nullable` annotations. *Limits:* Java only; must run on JDK 21 or newer (it can still target older releases); NullAway needs annotations. [Details](research/stack-go-rust-jvm-dotnet.md).
- **[Spotless](https://github.com/diffplug/spotless)**: `spotlessCheck` fails on unformatted code and `spotlessApply` fixes it; wraps google-java-format, ktlint, ktfmt and others behind one Gradle or Maven task. *Limits:* a build-tool plugin, not a standalone binary. [Details](research/stack-go-rust-jvm-dotnet.md).
- **[ArchUnit](https://github.com/TNG/ArchUnit)**: layers, cycles and naming rules written as JUnit tests; a violated rule fails the test run. *Limits:* a library inside your test suite; works on bytecode, so it has no source-level rules. [Details](research/stack-go-rust-jvm-dotnet.md).

### .NET

- **[.NET SDK analyzers](https://github.com/dotnet/sdk)**: built in, no extra package. Set `EnforceCodeStyleInBuild`, `AnalysisMode`, `TreatWarningsAsErrors`, run `dotnet format --verify-no-changes`, and make NuGet Audit warnings NU1903 and NU1904 errors for vulnerable packages. *Limits:* rule sets change with SDK versions, so pin `AnalysisLevel`; audit data comes from the GitHub Advisory Database. [Details](research/stack-go-rust-jvm-dotnet.md).

### Swift

- **[SwiftLint](https://github.com/realm/SwiftLint)**: style and convention rules built on SwiftSyntax; `--strict` fails on warnings, `--fix` corrects, SARIF/JSON/GitHub reporters, custom rules in config. *Limits:* it is a linter, not a formatter; pair with `swift-format` or SwiftFormat if you want enforced layout. [Details](research/stack-go-rust-jvm-dotnet.md).

### Shell

- **[ShellCheck](https://github.com/koalaman/shellcheck)**: bugs and portability problems in `sh`, `bash`, `dash` and `ksh`. *Limits:* a stable-tool exception, last release in August 2025 with ongoing commits; no zsh. jactionlint already runs it on workflow `run:` steps.

### Databases

- **[schemalens](https://github.com/mokevnin/schemalens)**: compares a Go model (ent, gorm, bun) with the live PostgreSQL, MySQL or SQLite schema and reports every disagreement as a structured finding, with JSON and SARIF output, a baseline and an agent skill. Checks things a structural diff does not: missing foreign-key indexes, constraints the model assumes but the database does not enforce, nullable columns for required fields. *Limits:* **maintained by the owner of this repository**; created 2026-10-20, v0.1.x, one maintainer, no outside users yet. Go models only. Compared with `database_consistency` (the Ruby/ActiveRecord original) and Atlas (structural diff and drift, a different job); no Go equivalent was found.
- **[squawk](https://github.com/sbdchd/squawk)**: finds PostgreSQL migrations that lock tables or cause downtime, with JSON output and no database needed. *Limits:* PostgreSQL only, no autofix; SQLFluff covers style. Atlas lint is not adopted: its stronger checks need Atlas Pro and a login. [Details](research/cross-cutting.md).

### Custom rules

- **[ast-grep](https://github.com/ast-grep/ast-grep)**: project-specific syntax rules as YAML, with tests for the rules themselves (`ast-grep test`). *Limits:* syntax only, no data-flow analysis.

### Secrets

- **[Betterleaks](https://github.com/betterleaks/betterleaks)**: finds committed secrets in files, git history and pull requests, with optional live validation of credentials. Chosen over Gitleaks because it reads the same kind of TOML rules and `gitleaks:allow` comments and is still released, while Gitleaks has had no release since March 2026 (v8.30.1). Its README says it is maintained by the people behind Gitleaks. *Limits:* created February 2026; the stable line is v1.9.0 while v2 is in release-candidate, so pin the version; recall claims are the project's own; TruffleHog (AGPL-3.0) and Kingfisher (Apache-2.0) are the alternatives. [Details](research/cross-cutting.md#1-secrets-scanning).

### Vulnerabilities

- **[OSV-Scanner](https://github.com/google/osv-scanner)**: known vulnerabilities in lockfiles and SBOMs across many ecosystems, with call analysis to reduce noise. *Limits:* not an image scanner; if you scan container images use Trivy (never `trivy-action` by tag, pin to a version or digest after the March 2026 compromise) or Grype. [Details](research/cross-cutting.md#2-vulnerabilities-and-sca).

### Docker, Terraform and Kubernetes

- **[Hadolint](https://github.com/hadolint/hadolint)**: Dockerfile best practices. *Limits:* GPL-3.0; security-focused IaC checks belong to Trivy or Checkov. [Details](research/cross-cutting.md).
- **[TFLint](https://github.com/terraform-linters/tflint)**: Terraform correctness and provider-specific rules through plugins. *Limits:* `tflint --init` downloads plugins, so pin them; for IaC security add Trivy `config` (if you already run Trivy) or Checkov (no clear winner). [Details](research/cross-cutting.md).
- **[Kubeconform](https://github.com/yannh/kubeconform)**: validates Kubernetes manifests against API and CRD schemas. *Limits:* validity only; last release June 2026. [Details](research/cross-cutting.md).

### Config files

- **[check-jsonschema](https://github.com/python-jsonschema/check-jsonschema)**: validates YAML, JSON and TOML against JSON Schema, with ready hooks for common formats. *Limits:* mostly a one-maintainer project; remote schemas need network or vendoring; style rules need yamllint. [Details](research/cross-cutting.md).

### Policy

- **[Conftest](https://github.com/open-policy-agent/conftest)**: your own rules in Rego over YAML, JSON, HCL, Dockerfile, CODEOWNERS and 15 more formats. *Limits:* Rego is harder to write than YAML rules; exit code and SARIF output were not verified. Kyverno is for Kubernetes admission only. [Details](research/cross-cutting.md).

### Agent configuration

- **[agnix](https://github.com/agent-sh/agnix)**: lints CLAUDE.md, AGENTS.md, SKILL.md, hooks and MCP configs for Claude Code, Codex, Cursor, Copilot, OpenCode and Kiro, with `--fix`. Tested: errors exit 1; warnings exit 0 unless `--strict` is passed. *Limits:* created January 2026, one main maintainer; rules track fast-changing vendor formats. [Details](research/cross-cutting.md).

### Git conventions

- **[commitlint](https://github.com/conventional-changelog/commitlint)**: Conventional Commits for a message, a hook or a CI range. *Limits:* needs Node; checks format, not accuracy.

### Documentation

- **[markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2)**: Markdown style and structure. *Limits:* no prose or spelling checks.
- **[lychee](https://github.com/lycheeverse/lychee)**: broken links. *Limits:* network flakiness; give it a GitHub token and a cache.
- **[typos](https://github.com/crate-ci/typos)**: low-noise spell checking of source code and docs. *Limits:* finds only known misspellings.

<!-- tools:end -->

## Under review

These categories matter but have **no recommendation yet**: the candidates were not compared well enough. Names are research leads, not endorsements. Working notes are in [`research/`](research/).

| Category | Candidates | Why it is still open |
|---|---|---|
| JavaScript / TypeScript extras | Oxlint with oxfmt, Biome, publint, arethetypeswrong, size-limit, syncpack, Stylelint, axe-core | ESLint and Prettier are recommended; Oxlint is the fast alternative but exits 0 on warnings unless `--deny-warnings`, and typescript-eslint does not support TypeScript 7 yet. The package-hygiene tools apply only to libraries. |
| Python types | Pyrefly, pyright, mypy, ty | No clear winner; ty is beta. |
| Ruby types, boundaries, security | Sorbet, Steep, Packwerk, Brakeman | Brakeman is free for non-commercial use only. Type checkers need a clearer comparison. |
| PHP extras | Rector, composer-dependency-analyser, Psalm | Exit codes and maintenance not confirmed. |
| Kotlin, .NET, Elixir | ktlint, detekt, Konsist, Meziantou.Analyzer, ArchUnitNET, Credo, Sobelow, Dialyxir | Stable releases are old or pre-1.0, or confidence is low. |
| Container images | Trivy, Grype | Trivy's GitHub Action and a release were compromised in March 2026 ([advisory](https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23)); no clear winner yet. |
| IaC and Kubernetes security | Checkov, Trivy config, kube-linter | Overlapping rules, no clear winner. |
| Custom rules with data-flow | Opengrep, Semgrep | Opengrep is a community fork; its cross-file limits and licence trade-offs need a closer look. |
| Git hooks | prek, hk, pre-commit, Lefthook | prek is the leading candidate (drop-in for pre-commit) but is pre-1.0; hk is the choice of some mise-based projects. |
| API contracts | Spectral, vacuum, Redocly CLI, Buf | Overlapping rulesets. |
| SQL style | SQLFluff | Style and migration safety are different jobs; not yet reviewed. |
| Architecture, other ecosystems | go-arch-lint, arch-go, tach | No clear winner for Go. |
| YAML style | yamllint | Not yet compared with schema validation. |
| Licences and supply chain | REUSE, Scorecard, Syft, ScanCode Toolkit | Mostly reporting tools; need an enforcement angle. |

## How this list is kept current

- [`tools.json`](tools.json) records the last review date, sources, rationale and limitations of each tool.
- A [weekly workflow](.github/workflows/freshness.yml) flags archived repositories, old pushes and stale releases. It is a signal, not a verdict: a quiet repository can be a finished one, and a busy one can be the wrong choice.
- Replacements need a written comparison. See [CONTRIBUTING.md](CONTRIBUTING.md).
- [`research/`](research/) holds working notes per stack (JavaScript, Python/Ruby/PHP, Go/Rust/JVM/.NET, cross-cutting). They are research leads: several tools there were compared on documentation only and are **not** recommendations until they appear in the list above.
- Tools we looked at and did not take are in [docs/not-adopted.md](docs/not-adopted.md).
- Reusable setup patterns (hooks, CI, generated-code gates) are in [docs/patterns.md](docs/patterns.md).

## License

[CC0 1.0](LICENSE): public domain. Take what is useful.

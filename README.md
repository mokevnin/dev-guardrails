# Dev Quality Gates

An opinionated, continuously curated list of tools for **enforcing** software development standards.

Dev Quality Gates is not an Awesome List. It does not list every linter for every language. For each job it recommends one tool (rarely two), says why, and says where the tool stops working.

## Principles

- **Opinionated.** One recommended tool per job. Several only when the jobs or the environments really differ.
- **Curated.** Every tool is checked against the [selection criteria](CONTRIBUTING.md#selection-criteria) before it is listed, and again on a schedule.
- **Coverage over quantity.** A tool that replaces three narrow checks beats three narrow tools.
- **Fast native toolchains first.** Modern stacks are converging on Rust-native tools that do lint, format and analysis in one binary (Ruff, Oxlint with oxfmt, Mago, rumdl). We prefer them over a pile of older single-purpose tools when they cover the same ground. Ecosystems without one (Ruby, Java, .NET, Swift) keep their standard tools.
- **Enforcement over advice.** A tool must fail a build (non-zero exit code) when a standard is violated. Reports that nobody reads do not count.
- **Agent-friendly.** Non-interactive, machine-readable output, clear diagnostics, and autofix where it is safe. AI coding agents are first-class users of these tools.
- **Honest about gaps.** A category with no verified recommendation stays empty rather than getting an outdated one.

This is **not a universal stack**. Do not install everything here. Pick the entries that match your project.

## Use it in your project

Ask your coding agent, from the root of your repository:

```text
Apply https://github.com/mokevnin/dev-quality-gates to this repository.
Read and follow https://raw.githubusercontent.com/mokevnin/dev-quality-gates/main/docs/adopt.md.
Show me the plan before you change anything.
```

The agent inspects the project, picks only the entries that fit, shows you the plan, wires the checks into hooks and CI, and proves that each one can fail. The instructions are in [docs/adopt.md](docs/adopt.md); to do it yourself, pick entries below by language and by cross-cutting category, then use the [setup patterns](docs/patterns.md).

## Recommendations

The entries below are **generated from [`tools.json`](tools.json)** (`pnpm run readme`), which records the review date, sources, rationale and limitations of each tool. Every entry was first checked on 2026-10-23: that is one sweep, not independent reviews. Where a claim was tested by running the tool, the entry says so; otherwise it rests on documentation and repository activity.

<!-- tools:start -->

### GitHub Actions

- **[jactionlint](https://github.com/jdx/jactionlint)**: lints workflows, composite actions and `dependabot.yml` for correctness, security and policy in one binary. It is a fork of actionlint whose security rules follow the audits of zizmor, so you do not need `actionlint` or `zizmor` next to it by default. `--fix` repairs what has a mechanical fix; with `--online` it also pins tags to commit SHAs. *Limits:* created in October 2026 and run by one maintainer; parity with zizmor is self-reported. If you need an established second implementation, offline archived-action detection, pre-commit config audits or an LSP, add [zizmor](https://github.com/zizmorcore/zizmor). [Details](research/github-actions.md).

### GitLab CI

- **[Plumber](https://github.com/getplumber/plumber)**: CI/CD security scanner for GitLab CI (and GitHub Actions): checks `.gitlab-ci.yml`, resolved includes and project settings such as branch protection, and reports to the terminal, JSON, SARIF and GitLab SAST. Runs locally, in Docker or as a GitLab CI component. The only widely adopted GitLab pipeline scanner found: 829 stars, 30 releases, v0.7.11 on 2026-10-21, MPL-2.0, used by projects such as Delve and Resty. *Limits:* Created 2026-01-19 and pre-1.0. A security and compliance scanner, not a syntax checker: use GitLab's own CI Lint (also `glab ci lint`) for syntax. Its exit codes were not checked here. For GitHub Actions we recommend jactionlint instead.

### JavaScript and TypeScript

- **[Knip](https://github.com/webpro-nl/knip)**: unused files, exports and dependencies. *Limits:* monorepos need configuration; never run `--fix` unattended.
- **[Oxlint and oxfmt](https://github.com/oxc-project/oxc)**: Rust-native linter and formatter from the Oxc toolchain: Oxlint runs ESLint-compatible rules (type-aware ones need TypeScript 7), oxfmt is the Prettier-compatible formatter. One fast toolchain instead of ESLint plus Prettier; releases weekly (oxlint 1.89, oxfmt 0.74 on 2026-10-19). *Limits:* oxfmt is pre-1.0. Oxlint exits 0 on warnings, so pass `--deny-warnings` in CI (tested). Per its docs, Vue, Svelte and Angular template files are not linted and the plugin ecosystem is smaller than ESLint's: keep ESLint only where you depend on those. [Details](research/stack-javascript.md).
- **[TypeScript](https://github.com/microsoft/TypeScript)**: `tsc --noEmit` with `strict`; version 7 is the native, much faster compiler. *Limits:* the TypeScript 7 compiler API is not ready, so tools that import `typescript` may need TypeScript 6 beside it. `microsoft/typescript-go` is archived because it was merged, not abandoned. [Details](research/stack-javascript.md).
- **[dependency-cruiser](https://github.com/sverweij/dependency-cruiser)**: import-graph rules (forbidden paths, cycles, orphans, dev-deps in production code) with non-zero exit and JSON output; `--ignore-known` baselines legacy violations. Chosen over eslint-plugin-boundaries because it does not depend on the lint stack. *Limits:* static analysis misses dynamic imports; no autofix. [Details](research/stack-javascript.md).
- **[syncpack](https://github.com/JamieMason/syncpack)**: Rust tool that enforces one version of each dependency and consistent ranges across a monorepo; 11M downloads a month. *Limits:* monorepos only; package-manager catalogs reduce the need; sherif is the narrower alternative. [Details](research/ecosystem-gaps.md).

### Python

- **[Ruff](https://github.com/astral-sh/ruff)**: linter and formatter that replaces Flake8, isort, pyupgrade and Black. *Limits:* no type checking, no custom-rule plugins. The `S` rules replace Bandit, `D` replaces pydocstyle (archived) and `C901` replaces xenon and radon; pair with vulture for dead code across modules.
- **[ty](https://github.com/astral-sh/ty)**: Rust-native Python type checker and language server from the authors of Ruff and uv. The most starred of the new checkers (19.9k stars) and downloaded as much as pyright (about 41 million PyPI downloads a month); v0.0.91 on 2026-10-22. *Limits:* Beta: 0.0.x, so new releases can add type errors; pin the version. mypy (160 million downloads) and pyright are the stable, battle-tested choices, and Pyrefly (Meta, stable 1.4, 7.1k stars) is the other Rust option.
- **[deptry](https://github.com/osprey-oss/deptry)**: unused, missing and transitive dependencies. *Limits:* static analysis misses dynamic imports.
- **[import-linter](https://github.com/seddonym/import-linter)**: import contracts (layers, forbidden, independence, protected) that fail CI. *Limits:* checks imports only; [tach](https://github.com/tach-org/tach) is the alternative for public-interface rules. [Details](research/stack-python-ruby-php.md).
- **[django-upgrade](https://github.com/adamchainz/django-upgrade)**: rewrites code to the idioms of your target Django version, and fails CI when files would change. *Limits:* Django only; narrow by design. [Details](research/ecosystem-gaps.md).
- **[django-migration-linter](https://github.com/3YOURMIND/django-migration-linter)**: flags Django migrations that are not backward compatible with the running code (`lintmigrations`); 3.4M downloads a month. *Limits:* Django only; not verified by running; does not replace squawk for lock analysis on SQL. [Details](research/ecosystem-gaps.md).

### Go

- **[golangci-lint](https://github.com/golangci/golangci-lint)**: one runner for the Go linters and the formatter, with `golangci-lint custom` for your own analyzers. *Limits:* choose linters deliberately; GPL-3.0.
- **[govulncheck](https://github.com/golang/vuln)**: reports known vulnerabilities in the Go modules and standard library you actually call, with call stacks, from the official Go vulnerability database. *Limits:* with `-json` and `-format sarif` it exits 0 whatever it finds, so gate on the text output; blind to calls through `reflect`; the GitHub repo is a mirror of `golang.org/x/vuln`. For repos in several languages see the open Vulnerabilities decision. [Details](research/stack-go-rust-jvm-dotnet.md).
- **[go-arch-lint](https://github.com/fe3dback/go-arch-lint)**: architecture rules for Go in one `.go-arch-lint.yml`: components by path, and for each the components and vendor packages it may import. `go-arch-lint check` exits 1 on a violation (run) and has `--json`; an optional deep scan also checks method calls and injected dependencies. The Go counterpart of archspec and import-linter. Chosen over arch-go for 2x the stars and a steadier release pace. *Limits:* 616 stars, one main maintainer; no SARIF found. Import-level rules only, so a call-shape rule needs ast-grep. A component with no allowed imports still needs `mayDependOn` or a flag, so a leaf is declared with `anyVendorDeps` (run). [Details](research/ecosystem-gaps.md).

### Rust

- **[Clippy](https://github.com/rust-lang/rust-clippy)**: the official linter; run `cargo clippy -- -D warnings`. *Limits:* tied to the toolchain version.
- **[rustfmt](https://github.com/rust-lang/rustfmt)**: the official formatter; run `cargo fmt --check` in CI. *Limits:* versioned with the Rust toolchain, not through GitHub releases; style options are few by design. [Details](research/stack-go-rust-jvm-dotnet.md).
- **[cargo-machete](https://github.com/bnjbvr/cargo-machete)**: Finds unused dependencies in Cargo.toml quickly and without compiling, so it runs on stable Rust in CI. The most used of the three tools compared (1.4k stars; cargo-udeps 2.1k stars needs nightly, cargo-shear 577). *Limits:* Text-based search, so it can report false positives and misses macro-generated uses; ignore them in Cargo.toml metadata. Not a replacement for cargo-deny, which covers advisories and licences.
- **[cargo-deny](https://github.com/EmbarkStudios/cargo-deny)**: one policy file for RustSec advisories, licences, banned or duplicate crates and allowed registries; non-zero exit on violation. It replaces `cargo-audit` for the advisory check. *Limits:* checks metadata only, not dependency source; needs a maintained `deny.toml`. [Details](research/stack-go-rust-jvm-dotnet.md).

### Ruby

- **[RuboCop](https://github.com/rubocop/rubocop)**: linter and formatter with autocorrect and custom cops. *Limits:* slower than native-code linters. Add the `rubocop-rails`, `rubocop-rspec` (or `rubocop-minitest`) and `rubocop-performance` plugins as needed; Standard is a wrapper and not needed.
- **[strong_migrations](https://github.com/ankane/strong_migrations)**: stops unsafe Rails migrations (locking indexes, column drops, type changes) while they run and names the safe alternative; 4.4k stars, MIT, active. It checks Ruby migrations, so it does not overlap with squawk. *Limits:* PostgreSQL, MySQL and MariaDB only; runs only when migrations run, so CI must run them. [Details](research/ecosystem-gaps.md).
- **[Bullet](https://github.com/flyerhzm/bullet)**: detects N+1 queries and unused eager loading; with `Bullet.raise = true` in test the specs fail. The standard Rails tool (7.3k stars, 188M gem downloads). *Limits:* finds only what tests exercise. [Details](research/ecosystem-gaps.md).
- **[i18n-tasks](https://github.com/glebm/i18n-tasks)**: `i18n-tasks health` fails on missing, unused and inconsistent translation keys and normalises locale files. The mature Rails option. *Limits:* Ruby and Rails; last release 2025-11. [Details](research/ecosystem-gaps.md).
- **[Herb](https://github.com/marcoroth/herb)**: HTML-aware ERB parser with linter and formatter; replaces erb_lint, which has had no release since 2025-01. 600k npm downloads a month. *Limits:* pre-1.0; formatter is experimental; the linter runs through npm. [Details](research/ecosystem-gaps.md).
- **[Sorbet](https://github.com/sorbet/sorbet)**: fast static type checker for Ruby (used by Stripe and Shopify); with tapioca it types gems and Rails. Chosen over Steep for adoption (158M vs 6.9M gem downloads). *Limits:* needs `sig` annotations and gradual strictness levels; Steep with RBS is the other direction. [Details](research/ecosystem-gaps.md).
- **[Packwerk](https://github.com/Shopify/packwerk)**: enforces package dependency and privacy rules in a Rails monolith. *Limits:* needs modularisation work; [pks](https://github.com/rubyatscale/pks) is a Rust drop-in claiming 10-20x speed but is very small (10 stars, unverified). [Details](research/ecosystem-gaps.md).
- **[ArchSpec](https://github.com/crmne/archspec)**: architecture rules in one `Archspec.rb`: components by glob, layers, `cannot_use`, `cannot_call`, naming, cycles and Rails presets (layered, hexagonal, modular monolith, CQRS). Needs no packages, unlike Packwerk. Run: `archspec check` exits 1 on a violation, `--format json` for agents; a todo file lets you adopt it in an existing app. *Limits:* created June 2026, one maintainer, 262 stars; no SARIF found. Static analysis only (Ruby 3.2+, Rubydex). Overlaps Packwerk for package boundaries: use one of them. [Details](research/custom-rules.md).

### PHP

- **[Mago](https://github.com/carthage-software/mago)**: Rust-native PHP toolchain: linter, formatter, static analyzer and architectural `guard` rules in one binary, with auto-fixes and a baseline. Replaces PHPStan, PHP-CS-Fixer and Deptrac; 30 releases, v1.58.2 on 2026-10-19. *Limits:* Created in October 2024, so younger than PHPStan; its framework-specific extensions (Laravel, Symfony) were not compared rule by rule. Check your framework's coverage before dropping PHPStan.
- **[Rector](https://github.com/rectorphp/rector)**: automated upgrades and refactoring sets; `--dry-run` in CI shows pending changes. A different job from Mago. *Limits:* depends on the rule sets you choose; fail-on-diff behaviour read from the docs only. [Details](research/ecosystem-gaps.md).

### Java

- **[Error Prone](https://github.com/google/error-prone)**: bug patterns checked by the Java compiler on every build; raise a check to `ERROR` to fail the build. With [NullAway](https://github.com/uber/NullAway) as a plugin it also enforces null safety from `@Nullable` annotations. *Limits:* Java only; must run on JDK 21 or newer (it can still target older releases); NullAway needs annotations. [Details](research/stack-go-rust-jvm-dotnet.md).
- **[Spotless](https://github.com/diffplug/spotless)**: `spotlessCheck` fails on unformatted code and `spotlessApply` fixes it; wraps google-java-format, ktlint, ktfmt and others behind one Gradle or Maven task. *Limits:* a build-tool plugin, not a standalone binary. [Details](research/stack-go-rust-jvm-dotnet.md).
- **[ArchUnit](https://github.com/TNG/ArchUnit)**: layers, cycles and naming rules written as JUnit tests; a violated rule fails the test run. *Limits:* a library inside your test suite; works on bytecode, so it has no source-level rules. [Details](research/stack-go-rust-jvm-dotnet.md).

### Kotlin

- **[detekt](https://github.com/detekt/detekt)**: Kotlin static analysis for complexity, smells and bugs, with baselines and SARIF. The de facto standard. *Limits:* stable release 1.23.8 is from 2025-02 and 2.0 is in alpha; ktlint formatting comes through spotless. [Details](research/ecosystem-gaps.md).

### .NET

- **[.NET SDK analyzers](https://github.com/dotnet/sdk)**: built in, no extra package. Set `EnforceCodeStyleInBuild`, `AnalysisMode`, `TreatWarningsAsErrors`, run `dotnet format --verify-no-changes`, and make NuGet Audit warnings NU1903 and NU1904 errors for vulnerable packages. *Limits:* rule sets change with SDK versions, so pin `AnalysisLevel`; audit data comes from the GitHub Advisory Database. [Details](research/stack-go-rust-jvm-dotnet.md).

### Swift

- **[SwiftLint](https://github.com/realm/SwiftLint)**: style and convention rules built on SwiftSyntax; `--strict` fails on warnings, `--fix` corrects, SARIF/JSON/GitHub reporters, custom rules in config. *Limits:* it is a linter, not a formatter; pair with `swift-format` or SwiftFormat if you want enforced layout. [Details](research/stack-go-rust-jvm-dotnet.md).

### Elixir

- **[Credo](https://github.com/rrrene/credo)**: the standard Elixir linter (consistency, readability, refactoring opportunities, custom checks); use with `mix format --check-formatted` and `mix compile --warnings-as-errors`. Where agents write the code, add the [ExSlop](https://github.com/elixir-vibe/ex_slop) plugin: Credo checks for what code generators over-produce (blanket `rescue`, `try` around a function that has a safe variant, N+1 queries, narrator docs and comments, roundabout `Enum` pipelines). Its findings fail the same `mix credo` run and come out in its JSON and SARIF (tested). *Limits:* style and smell rules, not type checking. ExSlop is young (created 2026-03, v0.4.x, one organisation); its `plugins:` line enables nothing when `.credo.exs` has an explicit `checks.enabled` list, so append `ExSlop.recommended_checks()` there instead. [Details](research/ecosystem-gaps.md).
- **[Sobelow](https://github.com/sobelow/sobelow)**: security scanner for Phoenix; `--exit` fails the build at a confidence level, SARIF output. Active again (0.16.0, 2026-09-30) after moving to this repository. *Limits:* Phoenix and Plug only; heuristic findings need a `.sobelow-skips` file. [Details](research/ecosystem-gaps.md).
- **[Dialyxir](https://github.com/jeremyjh/dialyxir)**: runs Dialyzer from Mix: success-typing analysis, including the check that each `@spec` matches its code (invalid contracts, functions with no local return). The Elixir 1.20 compiler infers types and fails on plain type errors, but does not read `@spec` (tested). `mix dialyzer` exits 2 on a warning, `--format github` annotates pull requests and an ignore file baselines old warnings. *Limits:* most useful where the project writes `@spec`; Dialyzer also works without specs, which the test did not cover. The first run builds the PLT (about 2.5 minutes for a toy project in the test), later runs take seconds, so cache the PLT in CI. No JSON or SARIF output; Assay offers both and incremental runs, but we did not run it and it is far smaller. What only Dialyzer catches shrinks as the compiler's type system grows. [Details](research/ecosystem-gaps.md).

### Shell

- **[ShellCheck](https://github.com/koalaman/shellcheck)**: bugs and portability problems in `sh`, `bash`, `dash` and `ksh`. *Limits:* a stable-tool exception, last release in August 2025 with ongoing commits; no zsh. jactionlint already runs it on workflow `run:` steps.

### Databases

- **[database_consistency](https://github.com/djezzzl/database_consistency)**: Ruby and Rails: compares ActiveRecord models with the database schema and reports missing null constraints, foreign keys and unique indexes, redundant indexes, mismatched enums and key types, and broken associations (20+ checkers). The established tool of its kind: v3.1.1 on 2026-10-22, 4.3 million gem downloads, MIT, supported by Pennylane. *Limits:* ActiveRecord only. Its exit code and machine-readable output were not checked. Go projects can use schemalens, which is modelled on it.
- **[schemalens](https://github.com/mokevnin/schemalens)**: compares a Go model (ent, gorm, bun) with the live PostgreSQL, MySQL or SQLite schema and reports every disagreement as a structured finding, with JSON and SARIF output, a baseline and an agent skill. Checks things a structural diff does not: missing foreign-key indexes, constraints the model assumes but the database does not enforce, nullable columns for required fields. *Limits:* **maintained by the owner of this repository**; created 2026-10-20, v0.1.x, one maintainer, no outside users yet. Go models only. Compared with database_consistency (the Ruby original, listed above) and Atlas (structural diff and drift, a different job); no Go equivalent was found.
- **[squawk](https://github.com/sbdchd/squawk)**: finds PostgreSQL migrations that lock tables or cause downtime, with JSON output and no database needed. *Limits:* PostgreSQL only, no autofix; SQLFluff covers style. Atlas lint is not adopted: its stronger checks need Atlas Pro and a login. [Details](research/cross-cutting.md).
- **[sqruff](https://github.com/quarylabs/sqruff)**: Rust-native SQL linter and formatter with SQLFluff-style rules, a `--dialect` per project and autofix. Chosen over SQLFluff as the fast single binary; v0.43.0 on 2026-10-22, Apache-2.0. *Limits:* Pre-1.0 and far smaller than SQLFluff (1.4k against 10k stars, 9 million PyPI downloads a month). Check your dialect before switching, and keep SQLFluff if you need its dbt and Jinja templating. Style only: use squawk for migration safety.

### API contracts

- **[oasdiff](https://github.com/oasdiff/oasdiff)**: Compares two OpenAPI specs and reports the changes that break existing API clients (`breaking`) or all consumer-visible changes (`changelog`), with a GitHub Action and a pre-commit hook. The standard backward-compatibility check for OpenAPI: 1.4k stars, v1.34.1 on 2026-10-21, Apache-2.0; rules are customizable. *Limits:* OpenAPI only (use Buf for protobuf). The exact option that makes CI fail on breaking changes was not checked here; read its docs. pb33f's openapi-changes is the smaller alternative.
- **[vacuum](https://github.com/daveshanley/vacuum)**: Single-binary linter for OpenAPI, AsyncAPI, Arazzo and JSON Schema that reads Spectral-style rulesets, so existing rules carry over. Chosen over Spectral and Redocly CLI as the fast native option with no Node dependency; v0.35.1 on 2026-10-23, MIT. *Limits:* Smaller community than Spectral (1.1k against 3.2k stars; Spectral and Redocly CLI each have 7 to 10 million npm downloads a month). Spectral compatibility has documented limits (see its README). Exits 2 when a rule times out, so incomplete runs are visible.
- **[Buf](https://github.com/bufbuild/buf)**: Protobuf lint, format and breaking-change detection against a previous version or git ref, in one CLI. The de facto standard for protobuf: 11.5k stars, v1.75.0 on 2026-10-22, Apache-2.0. *Limits:* Protobuf only. The Buf Schema Registry is an optional hosted service; lint and breaking-change checks run locally against a git ref.

### Web quality

- **[Stylelint](https://github.com/stylelint/stylelint)**: CSS, SCSS and CSS-in-JS linter with autofix and custom rules; 44M downloads a month. Oxlint does no CSS. *Limits:* CSS only. [Details](research/ecosystem-gaps.md).
- **[axe-core](https://github.com/dequelabs/axe-core)**: accessibility rules that fail tests when run through `@axe-core/playwright` (53M downloads a month). Static JSX checks are in Oxlint. *Limits:* finds only the automatable part of WCAG; needs a browser test suite; MPL-2.0. [Details](research/ecosystem-gaps.md).
- **[size-limit](https://github.com/ai/size-limit)**: fails the build when a bundle is over its size or load-time budget. *Limits:* needs a build step and budgets chosen by you. [Details](research/ecosystem-gaps.md).

### Tests and coverage

- **[diff-cover](https://github.com/Bachmann1234/diff_cover)**: Language-independent coverage gate: reads Cobertura, Clover, JaCoCo and lcov reports and fails when the coverage of the lines changed in a pull request is under a threshold, which is stricter in practice than a global floor. Works for any stack that can emit one of those formats; about 24 million PyPI downloads a month, v10.6.0 on 2026-09-22, Apache-2.0. *Limits:* Needs a coverage report from your test runner (coverage.py, vitest/c8, JaCoCo, llvm-cov, go-cover, and so on). Not a replacement for each ecosystem's own total threshold; set both. The exact flag and exit code were not checked here. Smaller community (849 stars) than the coverage tools it reads.

### Custom rules

- **[ast-grep](https://github.com/ast-grep/ast-grep)**: project-specific syntax rules as YAML (`pattern`, `inside`/`has`/`not`, `files`, `fix`), with tests for the rules themselves (`ast-grep test`). Give a rule `severity: error` to fail the build (run: warnings exit 0, errors exit 1); SARIF output for code scanning. Good for import-boundary and banned-call rules agents repeat. *Limits:* one file at a time: no cross-file resolution, types or data flow. Use a dependency or architecture tool for import graphs. [Details](research/custom-rules.md).
- **[easement](https://github.com/mokevnin/easement)**: one architecture config (`easement.yml`) for Go, TypeScript/JavaScript, Python and Java: components by path, an allow-list of dependencies, `public` APIs, cycles, and a `because` message shown with each violation. Reads real imports with tree-sitter and resolves them per language. `easement check` exits 1 on drift (run) and has `--format json`; a baseline fails on new violations and on fixed ones left in the file; `--diff origin/main` judges only what a pull request adds. *Limits:* **maintained by the owner of this repository**; v0.1.0 released 2026-10-25, one maintainer, no outside users yet. No SARIF (run: `--format sarif` exits 2). Imports only, so a call-shape rule needs ast-grep; external packages are not checked. Compared with dependency-cruiser, import-linter, ArchUnit and go-arch-lint, each of which is deeper in its own language; its advantage is one model and one baseline across several. Use those instead if the project is one language. [Details](research/custom-rules.md).

### Secrets

- **[Betterleaks](https://github.com/betterleaks/betterleaks)**: finds committed secrets in files, git history and pull requests, with optional live validation of credentials. Chosen over Gitleaks because it reads the same kind of TOML rules and `gitleaks:allow` comments and is still released, while Gitleaks has had no release since March 2026 (v8.30.1). Its README says it is maintained by the people behind Gitleaks. *Limits:* created February 2026; the stable line is v1.9.0 while v2 is in release-candidate, so pin the version; recall claims are the project's own; TruffleHog (AGPL-3.0) and Kingfisher (Apache-2.0) are the alternatives. [Details](research/cross-cutting.md#1-secrets-scanning).

### Vulnerabilities

- **[OSV-Scanner](https://github.com/google/osv-scanner)**: known vulnerabilities in lockfiles and SBOMs across many ecosystems, with call analysis to reduce noise. *Limits:* not an image scanner; if you scan container images use Trivy (never `trivy-action` by tag, pin to a version or digest after the March 2026 compromise) or Grype. [Details](research/cross-cutting.md#2-vulnerabilities-and-sca).

### Dependency updates

- **[Renovate](https://github.com/renovatebot/renovate)**: Dependency update bot that works on GitHub, GitLab, Bitbucket, Azure DevOps, Gitea and Forgejo, where Dependabot is GitHub-only. Policy lives in one config: pinning, grouping, and `minimumReleaseAge` to hold back freshly published versions. `renovate-config-validator` checks the config in CI. The most used of its kind: 22.8k stars, v44.181.0 on 2026-10-23, 1.7 million npm downloads a month. *Limits:* An update bot, not a gate: it opens pull requests and fails nothing by itself, so pair it with CI checks. AGPL-3.0 (using it, hosted or self-hosted, is fine; modifying and offering it as a service is not). Configuration is large; start from a shared preset. Dependabot is enough for a GitHub-only repository.

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

### Toolchain

- **[mise](https://github.com/jdx/mise)**: One tool for the project's whole toolchain, configured in `mise.toml`. It installs and pins tools (node, python, linters, hk; 1,000+ in the registry, from aqua, GitHub releases, npm, pypi, cargo and more) and switches versions per directory. It sets project environment variables and loads `.env` files and secrets. It runs tasks with dependencies and parallel runs under that same toolchain, and `mise lock` records versions, checksums and download URLs. `mise exec` and a GitHub Action give CI the same versions as developers; `mise bootstrap` can set up a whole machine. Same author as hk and jactionlint: `mise run check` is the single entry point here. *Limits:* It is an installer and task runner, not a checker, so it enforces nothing by itself. Tools installed from GitHub releases or language registries still need version pinning and review like any dependency.

### Git hooks

- **[hk](https://github.com/jdx/hk)**: Part of the mise ecosystem (same author): mise installs and pins the tools, hk runs them as Git hooks and CI checks from one `hk.pkl` file. About 170 ready-made steps ship in the box (`hk builtins`): Ruff, Biome, Oxlint, rustfmt, golangci-lint, RuboCop, shellcheck, hadolint, typos, zizmor, gitleaks and more, plus file hygiene checks (merge conflicts, large files, private keys). Steps run in parallel with file locks so fixers do not collide, and the same steps serve the hook (`hk check`, `hk fix`) and CI (`hk check --all`). *Limits:* Builtins only run a tool, they do not install it: pin the linters in `mise.toml`. Config is Pkl, so the pre-commit hook catalogue is not reused; prek and Lefthook are far more widely used. Hooks can be bypassed with `--no-verify`, so run `hk check --all` in CI. [Details](research/rust-native.md).

### Git conventions

- **[commitlint](https://github.com/conventional-changelog/commitlint)**: Enforces Conventional Commits on a message, a hook or a CI range (`--from/--to`), with shareable configs. The standard by a wide margin: 18.8k stars, about 44 million npm downloads a month, v21.2.4 on 2026-10-18. Needed if releases or changelogs are generated from commits. *Limits:* Requires Node. Checks format only, not whether the message is accurate. Compared on 2026-10-23 with the Rust options cocogitto (1.2k stars, last push 2026-04), convco (329 stars) and committed (185 stars, last release 2026-02): none has the adoption or the release pace, so Node remains the main cost. Python projects without Node can use commitizen.

### Documentation

- **[lychee](https://github.com/lycheeverse/lychee)**: broken links. *Limits:* network flakiness; give it a GitHub token and a cache.
- **[typos](https://github.com/crate-ci/typos)**: low-noise spell checking of source code and docs. *Limits:* finds only known misspellings.
- **[rumdl](https://github.com/rvben/rumdl)**: Rust-native Markdown linter and formatter that reads markdownlint configuration, so migration is cheap. `rumdl check` exits 1 on violations, `rumdl fmt` fixes; has a GitHub Action. Chosen over markdownlint-cli2 as the fast single-binary option. *Limits:* Pre-1.0 (v0.3.0). Compatibility with markdownlint is the project's own claim; custom JavaScript rules written for markdownlint are not expected to carry over.

<!-- tools:end -->

## Under review

These categories matter but have **no recommendation yet**: the candidates were not compared well enough. Names are research leads, not endorsements. Working notes are in [`research/`](research/).

| Category | Candidates | Why it is still open |
|---|---|---|
| JavaScript dead code and architecture | fallow, knip, dependency-cruiser | fallow is a Rust all-in-one (dead code, cycles, boundaries, duplication) and could replace both of our picks, but it is 7 months old, has 5.6 million npm downloads a month against knip's 69 million, and its plugin coverage is unverified. |
| JavaScript / TypeScript extras | Biome, publint, arethetypeswrong | Oxlint with oxfmt is recommended; Biome is the other Rust toolchain. publint and arethetypeswrong apply only to published libraries. |
| Ruby security | Brakeman | Free for non-commercial use only; commercial use needs a paid licence. |
| PHP dependencies | composer-dependency-analyser, composer-unused, ComposerRequireChecker | [Eight executed fixtures](research/composer-dependencies.md) favour the analyser for combined unused, shadow and misplaced dependency checks. Release 1.8.4 predates fixes on master; framework and dynamic-use limits still need evaluation. `composer audit` covers a different job. |
| Kotlin, .NET, Elixir extras | ktlint, Konsist, Roslynator, Meziantou.Analyzer, ArchUnitNET, Dialyxir | Stable releases are old or pre-1.0, or they overlap the picks above. |
| Container images | Trivy, Grype | Trivy's GitHub Action and a release were compromised in March 2026 ([advisory](https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23)); no clear winner yet. |
| Image layer efficiency | Dive | CI waste thresholds work, but `--json` bypasses them in v0.13.1. Last release March 2025; unresolved extraction-security and Docker compatibility reports. [Executed checks and alternatives](research/dive.md). |
| IaC and Kubernetes security | Checkov, Trivy config, kube-linter | Overlapping rules, no clear winner. |
| Custom rules with data-flow | Opengrep, Semgrep | Opengrep is a community fork; its cross-file limits and licence trade-offs need a closer look. |
| Architecture, other ecosystems | arch-go, tach | go-arch-lint is now listed; arch-go is the smaller Go alternative. tach is a Rust option for Python. |
| YAML style | yamllint | Not yet compared with schema validation. |
| Licences and supply chain | REUSE, Scorecard, Syft, ScanCode Toolkit | Mostly reporting tools; need an enforcement angle. |

## How this list is kept current

- [`tools.json`](tools.json) records the last review date, sources, rationale and limitations of each tool.
- A [weekly workflow](.github/workflows/freshness.yml) flags archived repositories, old pushes and stale releases. It is a signal, not a verdict: a quiet repository can be a finished one, and a busy one can be the wrong choice.
- Replacements need a written comparison. See [CONTRIBUTING.md](CONTRIBUTING.md).
- [`research/`](research/) holds working notes per stack (JavaScript, Python/Ruby/PHP, Go/Rust/JVM/.NET, cross-cutting). They are research leads: several tools there were compared on documentation only and are **not** recommendations until they appear in the list above.
- Tools we looked at and did not take are in [docs/not-adopted.md](docs/not-adopted.md).
- Step-by-step instructions for an agent that applies the list to a project are in [docs/adopt.md](docs/adopt.md).
- Reusable setup patterns (hooks, CI, generated-code gates) are in [docs/patterns.md](docs/patterns.md).

## License

[CC0 1.0](LICENSE): public domain. Take what is useful.

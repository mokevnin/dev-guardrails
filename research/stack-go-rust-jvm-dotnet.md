# Research: Go, Rust, JVM, .NET, Elixir, Swift

Date: 2026-10-23. Method: `gh api repos/...` (archived, pushed_at, stars, licence), latest release, registry JSON APIs (crates.io, Hex, NuGet, Maven `maven-metadata.xml`, Go module proxy), upstream README/docs, WebSearch for successors and incidents.

Conventions: "last push" is the repo's `pushed_at`; versions are verified against the registry unless marked. "Unverified" means read in a snippet or known from memory, not confirmed in a primary source today. I did not install or run any tool, so claims about false-positive rates, speed and exact exit codes are from docs only.

Notes on data quality:

- `search.maven.org` Solr results were stale (for example SpotBugs 4.9.3, Checkstyle 10.26.1). I used `repo1.maven.org/.../maven-metadata.xml` instead.
- GitHub reports `NOASSERTION` as licence for several multi-licence repos. I read the LICENSE file where it mattered.
- No 2026 supply-chain incident affecting the tools below turned up in my searches. That is "not found", not "none exist".

---

## Go

Existing recommendation: golangci-lint (v2.15.0, 2026-10-16, GPL-3.0, 19.5k stars, pushed 2026-10-21).

### Formatting and imports (gofumpt, gci)

| Candidate | Last release | Last push | Licence | Stars |
|---|---|---|---|---|
| [mvdan/gofumpt](https://github.com/mvdan/gofumpt) | v0.12.0, 2026-09-07 | 2026-10-12 | BSD-3-Clause | 4.1k |
| [daixiang0/gci](https://github.com/daixiang0/gci) | v0.14.0, 2026-02-28 | 2026-03-16 | BSD-3-Clause | 578 |

Verified in the golangci-lint docs: its formatter list is gci, gofmt, gofumpt, goimports, golines and swaggo, all with autofix. Recommendation: **no new entry.** Enable `gofumpt` and `gci` as formatters in the golangci-lint v2 config. Standalone binaries add nothing. Limit: I did not confirm the exact `golangci-lint fmt --diff` CLI behaviour (docs page did not show it).

### Vulnerabilities

| Candidate | Last release | Last push | Licence | Stars |
|---|---|---|---|---|
| [golang/vuln](https://github.com/golang/vuln) (govulncheck; module `golang.org/x/vuln`) | v1.9.0, 2026-10-11 (module proxy; GitHub "latest release" is a stale v1.1.4 because it is a mirror) | 2026-10-11 | BSD-3-Clause | 530 |
| OSV-Scanner (already in README "Under review") | v2.7.0, 2026-10-12 | 2026-10-23 | Apache-2.0 | 11.3k |

Verified (official `doc.go`, via search snippet): source mode does symbol-level reachability and prints call stacks; it reports conservatively for interface and function-pointer calls, is blind to `reflect` calls, and may miss things behind `unsafe`. **Gotcha:** text output exits non-zero on findings, but `-json`, `-format sarif` and `-format openvex` exit 0 regardless. A CI gate that wants machine-readable output must parse the result itself or run the text mode as a second step. It is not part of golangci-lint (not in the linter list).

Recommendation: **govulncheck for Go services.** It is the only candidate whose Go analysis is reachability-based by design (official Go team). It overlaps with OSV-Scanner, whose decision is still open in the README. Say so in the entry: for polyglot repos the OSV-Scanner decision applies. I did not verify whether OSV-Scanner does call analysis for Go.

### Test coverage threshold

[vladopajic/go-test-coverage](https://github.com/vladopajic/go-test-coverage): v2.20.1 (2026-10-22), pushed 2026-10-22, GPL-3.0 (LICENSE file read), 242 stars. One main maintainer (301 of ~400 contributions, rest is dependabot). README: fails when coverage is below a threshold, local-only, ~1 s run, coverage diff against base branch, badges, GitHub Action. No comparable specialised alternative found (the usual approach is `go tool cover` plus a shell script). Recommendation: **go-test-coverage**, with limits: bus factor of one, GPL-3.0 (same note as golangci-lint), thresholds measure lines not test quality. Confidence medium. Did not verify exit codes in the source or the per-file/package override syntax beyond README headings.

### Architecture

| Candidate | Last release | Last push | Licence | Stars |
|---|---|---|---|---|
| [fe3dback/go-arch-lint](https://github.com/fe3dback/go-arch-lint) | v1.19.0, 2026-09-07 | 2026-09-07 | MIT | 616 |
| [arch-go/arch-go](https://github.com/arch-go/arch-go) | v2.1.2, 2026-02-03 | 2026-10-21 | MIT | 280 |
| depguard (golangci-lint built-in) | v2.0.0, 2023-03-25 | 2026-10-23 | GPL-3.0 | 204 |

- go-arch-lint (README): component-based layering in `.go-arch-lint.yml` (components, allowed dependencies, common components), JSON output (`--json`).
- arch-go (README): dependency rules plus naming, content ("package may only contain interfaces") and function rules; compliance and coverage thresholds; `--json` and `--html` reports.
- depguard: import allow/deny lists per package glob; no layer model, but already inside the recommended runner.

**No clear winner** between go-arch-lint and arch-go; I would not propose either as the pick without running both on a real repo. For a simple "domain must not import infra" rule, depguard in golangci-lint is enough and adds no tool. Leaning: go-arch-lint for layer rules (more stars, purpose-built), arch-go if you also want naming and function rules. Not verified: exit codes, speed, Go-modules/workspace support.

### nilaway and staticcheck

- [uber-go/nilaway](https://github.com/uber-go/nilaway): 3.9k stars, pushed 2026-10-09, Apache-2.0, **no GitHub releases or tags** (module proxy only has a pseudo-version from 2026-09-18). README says "false positives and breaking changes can happen". Not built into golangci-lint; the wiki says the only supported route is a custom build via `golangci-lint custom` because of false positives. Recommendation: **do not adopt yet.** It fits the existing `golangci-lint custom` mechanism for teams who accept the noise; set `include-pkgs`.
- [dominikh/go-tools](https://github.com/dominikh/go-tools) (staticcheck): 2026.2.2 (2026-10-12), MIT, 6.9k stars. Already inside golangci-lint. Recommendation: no separate entry.
- gosec (v2.30.0, 2026-10-23, Apache-2.0), errcheck, revive are in the golangci-lint list (gosec, errcheck, revive verified in docs); no separate entries. `revive` moved to `revive-lint/revive`, 5.6k stars, v1.17.1.
- Go 1.26 rebuilt `go fix` on the analysis framework with modernizers (search sources, not primary). golangci-lint bundles modernize via `govet`. No separate tool.

Confidence: medium-high for the "no new entry" calls, medium for govulncheck and go-test-coverage. Not verified: golangci-lint SARIF/JSON options (not read today), staticcheck behaviour inside golangci-lint.

---

## Rust

Existing recommendation: Clippy.

### Formatter

[rust-lang/rustfmt](https://github.com/rust-lang/rustfmt): pushed 2026-10-22, Apache-2.0 (GitHub spdx; upstream is dual MIT/Apache, not read), 7.0k stars. GitHub's latest release is v1.6.0 from 2023: it ships with the toolchain via rustup and is versioned with Rust. This is the same situation as Clippy. `cargo fmt --check` exits non-zero on diffs (from memory, unverified today). Recommendation: **add rustfmt**, with the "versioned with the toolchain" limit and `stable_exception: true`. No real competitor.

### Dependency policy and advisories

| Candidate | Last release | Last push | Licence | Stars | crates.io |
|---|---|---|---|---|---|
| [EmbarkStudios/cargo-deny](https://github.com/EmbarkStudios/cargo-deny) | 0.20.2, 2026-07-09 | 2026-10-21 | Apache-2.0 (README: dual) | 2.5k | 6.7M downloads |
| [rustsec/rustsec](https://github.com/rustsec/rustsec) (cargo-audit) | cargo-audit 0.22.2, 2026-06-05 | 2026-10-19 | Apache-2.0/MIT (no spdx detected) | 2.0k | 13.8M |
| [mozilla/cargo-vet](https://github.com/mozilla/cargo-vet) | 0.10.3, 2026-10-22 | 2026-10-22 | Apache-2.0 OR MIT | 1.0k | 0.7M |

- cargo-deny (README): four checks, `advisories` (RustSec DB), `licenses`, `bans` (deny crates and duplicate versions), `sources` (registries and git). One `deny.toml`, non-zero exit on failure, official GitHub Action.
- cargo-audit: advisories only. A blog (unverified) says it has a `fix` subcommand that bumps versions, which cargo-deny lacks. cargo-deny already reads the same advisory DB, so running both gives overlap and, per one blog, occasionally conflicting answers.
- cargo-vet: requires humans to record audits (trust model), which is a process, not a drop-in check.

Recommendation: **cargo-deny** alone. It covers the cargo-audit job plus licence, ban and source policy. Limits: it checks metadata only (not source), and needs a policy file that you maintain. Add cargo-audit only if you need `cargo audit fix`/binary auditing (see below). cargo-vet is for organisations with an audit process; not proposed. cargo-auditable (v0.7.7, 2026-10-02) embeds dependency data in binaries so cargo-audit can scan them; useful, not a gate, not proposed.

### Unused dependencies

| Candidate | Last release | Last push | Licence | Stars |
|---|---|---|---|---|
| [Boshen/cargo-shear](https://github.com/Boshen/cargo-shear) | v1.14.0, 2026-09-22 | 2026-10-18 | MIT | 577 |
| [bnjbvr/cargo-machete](https://github.com/bnjbvr/cargo-machete) | v0.9.2, 2026-04-15 | 2026-10-19 | MIT | 1.4k |
| [est31/cargo-udeps](https://github.com/est31/cargo-udeps) | v0.1.61, 2026-04-29 | 2026-10-22 | MIT or Apache-2.0 (LICENSE file) | 2.1k |

- cargo-shear (README): static analysis, no compile; finds unused deps, deps in the wrong section (dev/build), and source files not reachable from the module tree; `--fix`; `--deny-warnings`; `--format=json`; flags ignores that suppress nothing; "feature-complete". Macro-generated imports need `--expand` (nightly, slow).
- cargo-machete (README): regex-based, fast, has a false-positive section and a `--with-metadata` mode (which can modify the lockfile/metadata, per README warning).
- cargo-udeps: README says it needs nightly to run. A search result claims it fails on recent cargo versions (unverified).

Recommendation: **cargo-shear.** It has autofix, JSON, strict exit and extra checks, and runs on stable. Limits: young (v1.x), static analysis misses macro-generated usage unless `--expand`; never run `--fix` unattended (same advice as Knip in the README). cargo-machete is a fine fallback (more stars, older); the two mostly overlap, so list only one.

### Semver and API compatibility

[obi1kenobi/cargo-semver-checks](https://github.com/obi1kenobi/cargo-semver-checks): v0.51.0 (2026-10-03), pushed 2026-10-20, Apache-2.0 OR MIT (README; GitHub shows Apache-2.0), 1.7k stars. Checks a library against its last published version for breaking changes using rustdoc JSON, with a documented exit status. Limits: libraries only; depends on the unstable rustdoc JSON format, so new Rust versions can lag; some changes (behaviour) are not detectable. The comparison candidate cargo-public-api (v0.52.0, 2026-05-25, MIT, 582 stars) lists and diffs the public API; I did not verify whether it can fail a build. Recommendation: **cargo-semver-checks for published libraries.** Confidence medium.

### Custom lints

[trailofbits/dylint](https://github.com/trailofbits/dylint): v6.2.0 (2026-10-16), pushed 2026-10-21, Apache-2.0, 700 stars. README: runs lints from user-supplied dynamic libraries, like Clippy; lint authors use `clippy_utils`, which has no stability guarantee. CI notes mention caching toolchains. Clippy has no custom-rule plugin, so this fills the "custom rules" column for Rust. Limit: lint libraries are tied to specific nightly compiler versions (README mentions toolchain downloads; the exact policy is unverified). For syntax-only rules, the README's existing ast-grep entry is simpler. Recommendation: **mention, do not add a README entry** unless the owner wants a Rust custom-rule line. Not compared to alternatives beyond ast-grep.

### Others checked

- cargo-geiger (now `geiger-rs/cargo-geiger`, geiger-0.14.0, 2026-10-12): reports `unsafe` usage; not verified whether it can fail a build. Not proposed.
- `cargo-llvm-cov` (v0.9.1, 2026-09-06, Apache-2.0 OR MIT?, licence not read) can enforce `--fail-under-lines`. From memory, unverified. Not proposed; worth a follow-up for a Rust coverage gate.
- No newer tool replacing several of these was found (search, standard + extended).

Confidence: medium-high on deny/shear picks, medium on semver. Not verified: cargo-deny CLI exit codes beyond the README's overview, cargo-shear performance claims, cargo-audit `fix`.

---

## JVM (Java, Kotlin)

### Java compile-time bug checks and null safety

| Candidate | Latest (registry) | Last push | Licence | Stars |
|---|---|---|---|---|
| [google/error-prone](https://github.com/google/error-prone) | v2.51.0, 2026-10-22 (Maven Central) | 2026-10-23 | Apache-2.0 | 7.3k |
| [uber/NullAway](https://github.com/uber/NullAway) | v0.14.3, 2026-10-22 (Maven Central) | 2026-10-23 | MIT | 4.1k |
| [spotbugs/spotbugs](https://github.com/spotbugs/spotbugs) | 4.10.5, 2026-10-12 | 2026-10-23 | LGPL-2.1 | 4.0k |

- Error Prone: javac plugin; checks run on every compile; per-check severity (`-Xep:Check:ERROR`, verified on its install page) so violations fail the build. Autofix via patching exists (I did not read the page, unverified). **Must run on JDK 21+** (verified), though it can compile older targets with `--release`.
- NullAway: an Error Prone plugin; JSpecify annotations; needs JDK 17+ and Error Prone 2.36+ (README). README claims under 10% build-time overhead.
- SpotBugs: bytecode analysis, works for any JVM language including Kotlin, plugins such as find-sec-bugs (from memory). Overlaps Error Prone for general bug patterns.

Recommendation: **Error Prone (with NullAway as the null-safety extra).** Fast, compile-time, low-noise. SpotBugs is not proposed by default (overlap); keep it as the choice for Kotlin/Groovy bytecode or for find-sec-bugs. Limits: Error Prone is Java only and needs JDK 21+ to run; NullAway needs annotations (work on legacy code).

### Formatting

[diffplug/spotless](https://github.com/diffplug/spotless): Gradle plugin 3.10.4 (2026-10-08), Maven plugin and CLI in the same repo, Apache-2.0, 5.7k stars. A wrapper that runs google-java-format, ktlint, ktfmt and others across languages, with `spotlessCheck` (fails) and `spotlessApply` (fixes) (from memory, I read only part of the README). Alternatives: [google/google-java-format](https://github.com/google/google-java-format) (v1.37.0, 2026-10-01, Apache-2.0 per file) and [facebook/ktfmt](https://github.com/facebook/ktfmt) (v0.65, 2026-10-07, Apache-2.0; repo is now `Kotlin/ktfmt`), which are engines, not enforcement gates, and Spotless wraps them. Recommendation: **Spotless.** Limits: build-tool plugin (Gradle/Maven), not a standalone binary for other build systems (a CLI exists, unverified).

### Style and code quality rules (Checkstyle vs PMD)

| Candidate | Latest | Last push | Licence | Stars |
|---|---|---|---|---|
| [checkstyle/checkstyle](https://github.com/checkstyle/checkstyle) | 14.3.0, 2026-09-27 | 2026-10-23 | LGPL-2.1 | 9.6k |
| [pmd/pmd](https://github.com/pmd/pmd) | 7.28.0, 2026-09-25 | 2026-10-23 | BSD-style (LICENSE read) | 5.5k |

- Checkstyle: formats `plain`, `xml`, `sarif` (verified on `cmdline.html`; exit code behaviour not documented there, unverified). Style, naming, Javadoc, imports, metrics; custom checks as Java classes.
- PMD: SARIF, JSON, CSV, XML, HTML and more (verified); rule categories for design, error-prone, performance; custom rules as XPath; also a copy-paste detector and other languages (from memory). Exit-code behaviour not confirmed in docs.

**No clear winner.** They overlap heavily, and the project's rule says not to recommend two tools that mostly do the same. If a single tool is wanted, PMD is slightly broader (smells, unused code, CPD, XPath rules), but Checkstyle is the standard for pure style and naming. Not proposed. Both are fast and CI-friendly; the choice depends on whether the team wants style rules (Checkstyle) or smell rules (PMD).

### Architecture

| Candidate | Latest | Last push | Licence | Stars |
|---|---|---|---|---|
| [TNG/ArchUnit](https://github.com/TNG/ArchUnit) | v1.5.1, 2026-09-25 | 2026-10-23 | Apache-2.0 | 3.9k |
| [LemonAppDev/konsist](https://github.com/LemonAppDev/konsist) | v0.18.1, 2026-10-10 | 2026-10-22 | Apache-2.0 | 1.7k |

ArchUnit: architecture rules as JUnit tests on bytecode (layers, cycles, naming); the test run fails the build. Konsist: Kotlin source-level rules as JUnit/Kotest tests, with a layer-check API (README); pre-1.0. Recommendation: **ArchUnit for Java**; **Konsist for Kotlin** when you need Kotlin-specific source rules. Both are libraries inside your test suite, not CLIs, so they need a JVM test setup. Not run.

### Kotlin lint and format

| Candidate | Latest | Last push | Licence | Stars |
|---|---|---|---|---|
| [detekt/detekt](https://github.com/detekt/detekt) | stable v1.23.8 (2025-02-21); 2.0.0-alpha.6 (2026-08-04) | 2026-10-23 | Apache-2.0 | 7.1k |
| [ktlint/ktlint](https://github.com/ktlint/ktlint) (formerly pinterest/ktlint) | 1.8.0 (2025-11-14); 2.0.0-ALPHA-4 (2026-08-21) | 2026-10-22 | MIT | 6.8k |
| [facebook/ktfmt](https://github.com/facebook/ktfmt) | v0.65, 2026-10-07 | 2026-10-20 | Apache-2.0 | 1.3k |

- detekt: static analysis (complexity, smells, style), baselines, SARIF/HTML/Markdown/Checkstyle reports (README), custom rules. The README now recommends the 2.0 line, still pre-release (alpha.6), with new Gradle plugin id `dev.detekt` and group `dev.detekt`. 1.23.x line is 20 months old. A search snippet says 2.0 needs Kotlin 2.4 (unverified). Pin the version either way.
- ktlint: lint plus built-in formatter, no config needed, `.editorconfig`, reporters `plain`, `json`, `html`, `checkstyle` (README; SARIF not listed), custom rule sets. Stable 1.8.0 is 11 months old; 2.0 is in alpha. Repo moved to the `ktlint` org; Maven group is still `com.pinterest.ktlint`.
- ktfmt: formatter only, no lint rules.

Recommendation: **ktlint for style and formatting, detekt for code-quality rules.** They do different jobs. Flag: both stable lines have gone quiet while 2.0 alphas are active, so state the version policy in the entry. Spotless can run ktlint or ktfmt; ktlint directly is simpler for Kotlin-only projects. Confidence medium. I did not verify Kotlin 2.x compatibility of 1.23.8/1.8.0.

### JVM dependency vulnerabilities

[dependency-check/DependencyCheck](https://github.com/dependency-check/DependencyCheck): v13.0.0 (2026-08-03), pushed 2026-10-22, Apache-2.0, 7.7k stars. **The old repo `jeremylong/DependencyCheck` is archived (pushed 2025-09-27, last release v12.1.0) and says "moved".** Maven Central `dependency-check-maven` is at 13.0.0 (2026-08-03). Search snippets: NVD API key strongly recommended (no key = very slow, 403 on shared key); Sonatype OSS Index switching to Sonatype Guide API tokens by end of 2026 (unverified). This overlaps with OSV-Scanner/Trivy (README "Under review"). Recommendation: **do not add a JVM-specific entry now;** decide with the OSV-Scanner vs Trivy vote. If kept, link the new repo, not the archived one. I did not verify how OSV-Scanner handles Gradle/Maven.

Other JVM items:

- OpenRewrite (`openrewrite/rewrite` v8.93.11, 2026-10-18; `rewrite-static-analysis` licence NOASSERTION): recipes that can fix and fail via dry-run; not verified; not proposed.
- JetBrains Qodana CLI (v2026.2.2): a platform that wraps IntelliJ inspections, mostly a commercial/linter hub; not evaluated beyond the repo check.
- No new unified Java/Kotlin tool replacing Checkstyle/PMD/SpotBugs/Error Prone found in 2026 searches (results were SEO listicles; not trusted).

---

## .NET (C#)

### Built-in analysis, formatting and NuGet audit

[dotnet/sdk](https://github.com/dotnet/sdk): v10.0.402 (2026-10-13), MIT, 3.2k stars; the old `dotnet/format` repo was consolidated into it (README read; not archived but frozen at v5.1.225507, 2021). Verified on Microsoft Learn:

- `EnforceCodeStyleInBuild=true` makes IDExxxx code-style rules run in build (off by default).
- `AnalysisMode` (`None` ... `All`) and `AnalysisLevel` select the CA rule set; `TreatWarningsAsErrors` / `-warnaserror` turns warnings into failures. Implicit IDE builds skip analysis unless TreatWarningsAsErrors is true.
- **NuGet Audit** runs during restore (.NET 8 SDK+): warnings NU1901-NU1904 (low to critical), configurable with `NuGetAuditMode`, `NuGetAuditLevel`, `NuGetAuditSuppress`; `NuGetAuditMode` defaults to `all` (transitive too) for net10.0+. Make it fail with `WarningsAsErrors` for NU1903;NU1904, ideally in a dedicated audit pipeline (docs suggest this). Data source is the GitHub Advisory Database.
- `dotnet list package --vulnerable` still exists (add `--include-transitive`), but NuGet Audit at restore is the integrated gate. `dotnet package update --vulnerable` is the .NET 10 fixer.
- `dotnet format --verify-no-changes` for formatting: standard practice (from memory, not re-read today).

Recommendation: **one entry for the .NET SDK built-ins** (analyzers, code-style-in-build, `dotnet format`, NuGet Audit as errors). It needs no extra package and is the baseline. Limit: rules are per-SDK-version, so pin `AnalysisLevel` to avoid surprise breaks on SDK upgrades.

### Extra analyzers

| Candidate | Latest (NuGet) | Last push | Licence | Stars |
|---|---|---|---|---|
| [meziantou/Meziantou.Analyzer](https://github.com/meziantou/Meziantou.Analyzer) | 3.0.316, 2026-10-21 | 2026-10-23 | MIT | 1.2k |
| [dotnet/roslynator](https://github.com/dotnet/roslynator) | 5.0.1, 2026-10-04 | 2026-10-04 | Apache-2.0 | 3.5k |
| [SonarSource/sonar-dotnet](https://github.com/SonarSource/sonar-dotnet) | SonarAnalyzer.CSharp 10.35.0.4138, 2026-09-28 | 2026-10-23 | SONAR Source-Available License v1.0 (LICENSE file read; not OSI-approved) | 921 |
| [DotNetAnalyzers/StyleCopAnalyzers](https://github.com/DotNetAnalyzers/StyleCopAnalyzers) | stable 1.1.118 (GitHub release, 2019-04-29); NuGet only has 1.3.x-beta | 2026-10-21 | MIT | 2.9k |
| [security-code-scan](https://github.com/security-code-scan/security-code-scan) | 5.6.7, 2022-09-05 | 2024-07-08 | LGPL-3.0 | 971 |

- Meziantou: API design, performance, security and usage rules; README links a comparison of duplicates with other analyzers. Plain NuGet package, rules are warnings, so `TreatWarningsAsErrors` fails them.
- Roslynator: a large analyzer set plus refactorings and a CLI (from memory, unverified).
- SonarAnalyzer: strong rule set, but the licence is source-available, not open source.
- StyleCop: style/layout rules only; the stable line is 7 years old and only betas ship.
- Security Code Scan: stale (last release 2022, last push 2024); should not be recommended.

Recommendation: **Meziantou.Analyzer** as the single add-on. It is MIT, active and designed to avoid duplicating others. Roslynator is a reasonable alternative; I did not compare rule coverage rule-by-rule, so the choice has medium confidence. Limits: rules are opinionated; tune severity in `.editorconfig`.

### Formatter alternative

[belav/csharpier](https://github.com/belav/csharpier): 1.3.0 (2026-06-07), MIT, 2.4k stars; opinionated, near-zero config formatter (`csharpier check`, from memory). `dotnet format` honours `.editorconfig` and is built in. **No clear winner**; default to built-in to avoid another tool. Not proposed.

### Architecture

| Candidate | Latest | Last push | Licence | Stars |
|---|---|---|---|---|
| [TNG/ArchUnitNET](https://github.com/TNG/ArchUnitNET) | 0.13.4 (GitHub 2026-08-19); NuGet also lists a `2.1.0-draft` | 2026-10-23 | Apache-2.0 | 1.4k |
| [BenMorris/NetArchTest](https://github.com/BenMorris/NetArchTest) | v1.3.2, 2021-05-23 (NuGet NetArchTest.Rules 1.3.2) | 2024-07-29 | MIT | 1.8k |

Recommendation: **ArchUnitNET** (active, from the ArchUnit family, tests in any test framework). NetArchTest is effectively dormant (no release since 2021, no push since mid-2024). Limits: ArchUnitNET is pre-1.0 and the odd `2.1.0-draft` NuGet entry should be checked before pinning (unverified what it is).

Confidence: high on the built-in baseline (primary docs), medium on Meziantou vs Roslynator. Not verified: `dotnet format` flags today, rule counts, performance.

---

## Elixir

| Candidate | Latest (Hex) | Last push | Licence | Stars | Hex downloads |
|---|---|---|---|---|---|
| [rrrene/credo](https://github.com/rrrene/credo) | 1.7.19, 2026-06-25 | 2026-10-21 | MIT | 5.2k | 93.7M |
| [jeremyjh/dialyxir](https://github.com/jeremyjh/dialyxir) | 1.4.8, 2026-09-05 | 2026-09-21 | Apache-2.0 | 1.8k | 92.5M |
| [sobelow/sobelow](https://github.com/sobelow/sobelow) | 0.16.0, 2026-09-30 | 2026-10-02 | Apache-2.0 | 66 | 42.8M |
| [mirego/mix_audit](https://github.com/mirego/mix_audit) | 2.1.5, 2025-06-09 | 2026-02-23 | BSD-3-Clause | 383 | 12.2M |

- **Sobelow moved:** `nccgroup/sobelow` (1.8k stars, last push 2024, last release v0.13.0 in 2023) is stale; Hex now links to `sobelow/sobelow` (organisation created 2025-05-08, same top contributors as the old repo, v0.16.0 on 2026-09-30). Verified: `--exit` returns non-zero at a confidence threshold, `--format json`, `--strict` exits 2 on parse failures. Phoenix-only. Link the new repo.
- Dialyxir (README): Dialyzer wrapper; exit status on warnings with `--ignore-exit-status` to opt out; ignore files; `--list-unused-filters` for CI. Type checking is Dialyzer's success typing, not full types.
- mix_audit (README): exits 1 when vulnerabilities are found, `--format json`; overlaps Hex's `mix hex.audit` (which only shows retired packages; README explains the difference).
- Credo: static analysis and consistency with custom checks and plugins (README not fully read; `--strict`, JSON and exit codes are from memory, unverified).
- Built-in (from memory, unverified today): `mix format --check-formatted`, `mix compile --warnings-as-errors`, `mix deps.unlock --check-unused`.

Recommendation: **Credo** (primary, clear winner as the only mainstream linter with 5.2k stars and active releases), **Sobelow** for Phoenix apps, **Dialyxir** if you want Dialyzer in CI. mix_audit is small and works, release is 16 months old; list as optional. No alternatives compared for Credo beyond ecosystem knowledge. Confidence medium-low (did not read the Credo and Elixir docs; I did not check how Elixir 1.20's type system changes the Dialyxir story).

---

## Swift

| Candidate | Latest | Last push | Licence | Stars |
|---|---|---|---|---|
| [realm/SwiftLint](https://github.com/realm/SwiftLint) | 0.65.1, 2026-08-21 | 2026-10-16 | MIT | 19.8k |
| [nicklockwood/SwiftFormat](https://github.com/nicklockwood/SwiftFormat) | 0.64.1, 2026-10-22 | 2026-10-23 | MIT | 8.9k |
| [swiftlang/swift-format](https://github.com/swiftlang/swift-format) | 604.0.0, 2026-09-16 | 2026-10-23 | Apache-2.0 | 3.0k |

- SwiftLint (README): rules mostly on SwiftSyntax; `--strict` and `--fix` (pre-commit snippet), reporters including `sarif`, `json`, `github-actions-logging`, `junit`, `checkstyle`; custom rules in config.
- SwiftFormat (README): `--lint` returns a non-zero code when changes are needed; reporters such as `github-actions-log`; Docker image.
- swift-format (README): official, distributed with the Swift toolchain; `lint --strict` turns warnings into failures; also `format`.

Recommendation: **SwiftLint** for rules (clear winner by activity and breadth). For formatting there is **no clear winner**: swift-format is official and bundled with the toolchain; SwiftFormat has more rules and options. SwiftLint plus one formatter is enough. I would propose SwiftFormat only if the owner wants one formatter pick; here I propose SwiftLint only. Not verified: SwiftLint run time on large repos, rule overlap between SwiftLint's `--fix` and the formatters.

---

## Deprecated, moved or risky (for docs/not-adopted.md or entry notes)

| Item | Finding |
|---|---|
| `jeremylong/DependencyCheck` | Archived 2025-09-27, moved to `dependency-check/DependencyCheck`. |
| `nccgroup/sobelow` | Stale (2024); moved to `sobelow/sobelow`. |
| `pinterest/ktlint` | Moved to `ktlint/ktlint`; Maven group unchanged. |
| `dotnet/format` | Consolidated into `dotnet/sdk`; last release 2021. |
| `BenMorris/NetArchTest` | No release since 2021; prefer ArchUnitNET. |
| `security-code-scan` | Last release 2022, last push 2024. |
| StyleCop.Analyzers | Stable release 2019; only betas on NuGet. Still receives commits. |
| `google/go-licenses` | v2.0.1 2025-09, push 2026-07; not evaluated. |
| `golang/vuln` GitHub "latest release" | Stale v1.1.4 (2025-01); real releases are tags on `golang.org/x/vuln`. Freshness checkers that read GitHub releases will misreport it. |
| `uber-go/nilaway` | No releases at all; pseudo-versions only. |
| `rust-lang/rustfmt` | GitHub latest release is v1.6.0 (2023); versioned with the toolchain. Needs `stable_exception`. |
| detekt, ktlint | Stable lines are 20 and 11 months old; 2.0 alphas are the active ones. |
| OWASP dependency-check, NVD | Needs an NVD API key; slow without it. |

Note for the registry freshness workflow: Clippy, rustfmt and govulncheck do not publish GitHub releases that reflect their real versions. Error Prone, NullAway and Spotless publish Maven artifacts, and Spotless GitHub tags look like `maven/3.10.4`.

---

## Summary of picks

| Job | Pick | Confidence |
|---|---|---|
| Go format/imports | golangci-lint formatters (gofumpt, gci), no new entry | high |
| Go vulns | govulncheck | medium |
| Go coverage | go-test-coverage | medium |
| Go architecture | no clear winner (go-arch-lint, arch-go); depguard for simple bans | low |
| Go nil panics | not now (nilaway) | medium |
| Rust format | rustfmt | high |
| Rust dependency policy | cargo-deny | high |
| Rust unused deps | cargo-shear | medium |
| Rust semver | cargo-semver-checks (libraries) | medium |
| Java bugs | Error Prone (+ NullAway) | high |
| Java/Kotlin format | Spotless | medium |
| Java style/smells | no clear winner (Checkstyle, PMD) | low |
| Java architecture | ArchUnit | high |
| Kotlin | ktlint (style) + detekt (smells), watch 2.0 lines | medium |
| Kotlin architecture | Konsist | medium |
| JVM vulnerabilities | defer to OSV-Scanner/Trivy decision; DependencyCheck moved | medium |
| .NET baseline | SDK analyzers, `dotnet format`, NuGet Audit | high |
| .NET extra analyzer | Meziantou.Analyzer | medium |
| .NET architecture | ArchUnitNET | medium |
| Elixir | Credo, Sobelow (Phoenix), Dialyxir | medium-low |
| Swift | SwiftLint; formatter has no clear winner | medium |

What I did **not** verify: that any tool runs cleanly on a real project; exit codes for Credo, Checkstyle, PMD, cargo-deny, rustfmt, `dotnet format`; JSON/SARIF output for go-arch-lint, Credo, ktlint (SARIF) and Error Prone; the `cargo-audit fix` and cargo-udeps breakage claims (blog/search snippets only); whether OSV-Scanner matches govulncheck reachability or DependencyCheck coverage; Elixir 1.20 type-system impact; Qodana and OpenRewrite in any depth.

---

## Proposed README entries

Ready to paste, in the repo's entry format. Place each under its category (new headings for Java, Kotlin, .NET, Elixir, Swift).

### Go

```markdown
- **[govulncheck](https://github.com/golang/vuln)**: reports known vulnerabilities in the Go modules and standard library you actually call, with call stacks, from the official Go vulnerability database. *Limits:* with `-json` and `-format sarif` it exits 0 whatever it finds, so gate on the text output; blind to calls through `reflect`; the GitHub repo is a mirror of `golang.org/x/vuln`. For repos in several languages see the open Vulnerabilities decision.
- **[go-test-coverage](https://github.com/vladopajic/go-test-coverage)**: fails the build when total, per-package or per-file test coverage drops below a threshold, locally with no service, and can compare against the base branch. *Limits:* GPL-3.0, one main maintainer; measures coverage, not test quality.
```

### Rust

```markdown
- **[rustfmt](https://github.com/rust-lang/rustfmt)**: the official formatter; run `cargo fmt --check` in CI. *Limits:* versioned with the Rust toolchain, not through GitHub releases; style options are few by design.
- **[cargo-deny](https://github.com/EmbarkStudios/cargo-deny)**: one policy file for RustSec advisories, licences, banned or duplicate crates and allowed registries; non-zero exit on violation. It replaces `cargo-audit` for the advisory check. *Limits:* checks metadata only, not dependency source; needs a maintained `deny.toml`.
- **[cargo-shear](https://github.com/Boshen/cargo-shear)**: unused and misplaced dependencies and unlinked source files, with `--fix`, `--deny-warnings` and JSON output; works on stable Rust without compiling. *Limits:* macro-generated imports need `--expand` (nightly, slow); do not run `--fix` unattended.
- **[cargo-semver-checks](https://github.com/obi1kenobi/cargo-semver-checks)**: for libraries you publish, fails on API changes that break semver compared with the last release. *Limits:* libraries only; relies on unstable rustdoc JSON, so a new Rust release can lag.
```

### Java and Kotlin

```markdown
- **[Error Prone](https://github.com/google/error-prone)**: bug patterns checked by the Java compiler on every build; raise a check to `ERROR` to fail the build. With [NullAway](https://github.com/uber/NullAway) as a plugin it also enforces null safety from `@Nullable` annotations. *Limits:* Java only; must run on JDK 21 or newer (it can still target older releases); NullAway needs annotations.
- **[Spotless](https://github.com/diffplug/spotless)**: `spotlessCheck` fails on unformatted code and `spotlessApply` fixes it; wraps google-java-format, ktlint, ktfmt and others behind one Gradle or Maven task. *Limits:* a build-tool plugin, not a standalone binary.
- **[ArchUnit](https://github.com/TNG/ArchUnit)**: layers, cycles and naming rules written as JUnit tests; a violated rule fails the test run. *Limits:* a library inside your test suite; works on bytecode, so it has no source-level rules.
- **[ktlint](https://github.com/ktlint/ktlint)**: Kotlin style linter with a built-in formatter, `.editorconfig` support and custom rule sets. *Limits:* the stable 1.8.0 dates from November 2025 and 2.0 is in alpha; Maven group is still `com.pinterest.ktlint`.
- **[detekt](https://github.com/detekt/detekt)**: Kotlin code-quality rules (complexity, smells) with baselines, SARIF output and custom rules. *Limits:* the stable 1.23.8 dates from February 2025 and the project recommends 2.0, still pre-release; pin the version.
- **[Konsist](https://github.com/LemonAppDev/konsist)**: Kotlin source-level architecture and convention rules as JUnit or Kotest tests. *Limits:* pre-1.0 (0.18); library inside your tests.
```

### .NET

```markdown
- **[.NET SDK analyzers](https://github.com/dotnet/sdk)**: built in, no extra package. Set `EnforceCodeStyleInBuild`, `AnalysisMode`, `TreatWarningsAsErrors`, run `dotnet format --verify-no-changes`, and make NuGet Audit warnings NU1903 and NU1904 errors for vulnerable packages. *Limits:* rule sets change with SDK versions, so pin `AnalysisLevel`; audit data comes from the GitHub Advisory Database.
- **[Meziantou.Analyzer](https://github.com/meziantou/Meziantou.Analyzer)**: extra Roslyn rules for API design, performance and usage, packaged as NuGet; findings fail the build under `TreatWarningsAsErrors`. *Limits:* opinionated, tune severity in `.editorconfig`; [Roslynator](https://github.com/dotnet/roslynator) is a comparable alternative that I did not compare rule by rule.
- **[ArchUnitNET](https://github.com/TNG/ArchUnitNET)**: architecture rules as tests in any .NET test framework. *Limits:* pre-1.0; NetArchTest has had no release since 2021.
```

### Elixir

```markdown
- **[Credo](https://github.com/rrrene/credo)**: static analysis and code-consistency checks for Elixir, with custom checks and plugins. *Limits:* advisory unless run with a strict mode and non-zero exit in CI; style-level, not type-level.
- **[Sobelow](https://github.com/sobelow/sobelow)**: security checks for Phoenix apps; `--exit` fails the build at a chosen confidence. *Limits:* Phoenix only; the repo moved from `nccgroup/sobelow`, which is stale.
- **[Dialyxir](https://github.com/jeremyjh/dialyxir)**: Dialyzer in `mix` with CI-friendly ignore files and unused-filter checks. *Limits:* success typing finds only definite errors; PLT build is slow on a cold CI cache.
```

### Swift

```markdown
- **[SwiftLint](https://github.com/realm/SwiftLint)**: style and convention rules built on SwiftSyntax; `--strict` fails on warnings, `--fix` corrects, SARIF/JSON/GitHub reporters, custom rules in config. *Limits:* it is a linter, not a formatter; pair with `swift-format` or SwiftFormat if you want enforced layout.
```

---

## Proposed tools.json records

```json
[
  {
    "id": "govulncheck",
    "repo": "golang/vuln",
    "category": "Go",
    "last_reviewed": "2026-10-23",
    "sources": [
      "https://go.googlesource.com/vuln/+/v1.7.0/cmd/govulncheck/doc.go",
      "https://proxy.golang.org/golang.org/x/vuln/@latest",
      "research/stack-go-rust-jvm-dotnet.md"
    ],
    "rationale": "Official Go vulnerability scanner with symbol-level reachability and call stacks. Latest v1.9.0 (2026-10-11) is published as a module tag.",
    "stable_exception": true,
    "limitations": "GitHub repo is a mirror and its latest GitHub release is stale (v1.1.4, 2025-01), so the freshness check misreads it. -json and -format sarif exit 0 regardless of findings. No reflect or some interface calls. Overlaps OSV-Scanner (open decision)."
  },
  {
    "id": "go-test-coverage",
    "repo": "vladopajic/go-test-coverage",
    "category": "Go",
    "last_reviewed": "2026-10-23",
    "sources": [
      "https://github.com/vladopajic/go-test-coverage",
      "research/stack-go-rust-jvm-dotnet.md"
    ],
    "rationale": "Fails the build when coverage falls below a configured threshold, with no external service, and can diff against the base branch. v2.20.1, 2026-10-22.",
    "limitations": "GPL-3.0. One main maintainer. Measures line coverage, not test quality. No comparable specialised alternative found; exit codes not verified in source."
  },
  {
    "id": "rustfmt",
    "repo": "rust-lang/rustfmt",
    "category": "Rust",
    "last_reviewed": "2026-10-23",
    "sources": ["https://github.com/rust-lang/rustfmt", "research/stack-go-rust-jvm-dotnet.md"],
    "rationale": "Official Rust formatter shipped with the toolchain; `cargo fmt --check` fails CI on unformatted code.",
    "stable_exception": true,
    "limitations": "Versioned with the Rust toolchain; the latest GitHub release (v1.6.0, 2023) is not meaningful. Few style options by design."
  },
  {
    "id": "cargo-deny",
    "repo": "EmbarkStudios/cargo-deny",
    "category": "Rust",
    "last_reviewed": "2026-10-23",
    "sources": [
      "https://embarkstudios.github.io/cargo-deny/",
      "https://crates.io/crates/cargo-deny",
      "research/stack-go-rust-jvm-dotnet.md"
    ],
    "rationale": "One policy file for RustSec advisories, licences, bans and allowed sources; covers the cargo-audit advisory check. 0.20.2, 2026-07-09, pushed 2026-10-21.",
    "limitations": "Checks metadata, not source. Needs a maintained deny.toml. cargo-audit remains useful only for `cargo audit fix` or binary auditing (unverified)."
  },
  {
    "id": "cargo-shear",
    "repo": "Boshen/cargo-shear",
    "category": "Rust",
    "last_reviewed": "2026-10-23",
    "sources": [
      "https://github.com/Boshen/cargo-shear",
      "https://crates.io/crates/cargo-shear",
      "research/stack-go-rust-jvm-dotnet.md"
    ],
    "rationale": "Static detection and --fix of unused and misplaced dependencies and unlinked source files, JSON output, no compile step, stable Rust. Preferred to cargo-machete (regex, more false positives) and cargo-udeps (needs nightly).",
    "limitations": "Macro-generated imports need --expand (nightly). Do not run --fix unattended. Young project (v1.14)."
  },
  {
    "id": "cargo-semver-checks",
    "repo": "obi1kenobi/cargo-semver-checks",
    "category": "Rust",
    "last_reviewed": "2026-10-23",
    "sources": [
      "https://github.com/obi1kenobi/cargo-semver-checks",
      "https://crates.io/crates/cargo-semver-checks",
      "research/stack-go-rust-jvm-dotnet.md"
    ],
    "rationale": "Fails on semver-breaking API changes against the last published release. v0.51.0, 2026-10-03.",
    "limitations": "Libraries only. Depends on unstable rustdoc JSON, so new Rust versions can lag. Behavioural breaks are not detected. cargo-public-api not compared for gating."
  },
  {
    "id": "error-prone",
    "repo": "google/error-prone",
    "category": "Java",
    "last_reviewed": "2026-10-23",
    "sources": [
      "https://errorprone.info/docs/installation",
      "https://repo1.maven.org/maven2/com/google/errorprone/error_prone_core/maven-metadata.xml",
      "https://github.com/uber/NullAway",
      "research/stack-go-rust-jvm-dotnet.md"
    ],
    "rationale": "Compile-time bug checks with per-check ERROR severity; NullAway plugin adds null-safety enforcement. Error Prone 2.51.0 (2026-10-22), NullAway 0.14.3 (2026-10-22).",
    "limitations": "Java only. Must run on JDK 21+ (can target older). NullAway needs @Nullable annotations. Overlaps SpotBugs; Checkstyle vs PMD has no clear winner and is not proposed."
  },
  {
    "id": "spotless",
    "repo": "diffplug/spotless",
    "category": "Java",
    "last_reviewed": "2026-10-23",
    "sources": [
      "https://github.com/diffplug/spotless",
      "research/stack-go-rust-jvm-dotnet.md"
    ],
    "rationale": "spotlessCheck fails on unformatted code, spotlessApply fixes; wraps google-java-format, ktlint, ktfmt and more. Gradle plugin 3.10.4 (2026-10-08).",
    "limitations": "Build-tool plugin (Gradle or Maven). GitHub tags look like maven/3.10.4, which may confuse freshness checks. check/apply tasks described from memory, not re-read."
  },
  {
    "id": "archunit",
    "repo": "TNG/ArchUnit",
    "category": "Java",
    "last_reviewed": "2026-10-23",
    "sources": [
      "https://github.com/TNG/ArchUnit",
      "https://repo1.maven.org/maven2/com/tngtech/archunit/archunit/maven-metadata.xml",
      "research/stack-go-rust-jvm-dotnet.md"
    ],
    "rationale": "Architecture rules (layers, cycles, naming) as JUnit tests that fail the build. v1.5.1, 2026-09-25.",
    "limitations": "Library inside the test suite; bytecode-level, so no source rules. Kotlin-specific source rules need Konsist."
  },
  {
    "id": "ktlint",
    "repo": "ktlint/ktlint",
    "category": "Kotlin",
    "last_reviewed": "2026-10-23",
    "sources": [
      "https://github.com/ktlint/ktlint",
      "https://repo1.maven.org/maven2/com/pinterest/ktlint/ktlint-cli/maven-metadata.xml",
      "research/stack-go-rust-jvm-dotnet.md"
    ],
    "rationale": "Kotlin linter with built-in formatter, .editorconfig support, json and checkstyle reporters, custom rule sets. Chosen over ktfmt (formatter only).",
    "stable_exception": true,
    "limitations": "Stable 1.8.0 is from 2025-11-14; 2.0.0-ALPHA-4 is active. Repository moved from pinterest/ktlint; Maven group unchanged. SARIF output not confirmed."
  },
  {
    "id": "detekt",
    "repo": "detekt/detekt",
    "category": "Kotlin",
    "last_reviewed": "2026-10-23",
    "sources": [
      "https://github.com/detekt/detekt",
      "https://detekt.dev/changelog-2.0.0/",
      "research/stack-go-rust-jvm-dotnet.md"
    ],
    "rationale": "Kotlin code-quality analysis with baselines, SARIF, custom rules. README now recommends the 2.0 line.",
    "stable_exception": true,
    "limitations": "Stable 1.23.8 is from 2025-02-21; 2.0.0-alpha.6 (2026-08-04) is pre-release with breaking changes expected and a new plugin id (dev.detekt). Kotlin 2.x compatibility of 1.23.8 not verified."
  },
  {
    "id": "konsist",
    "repo": "LemonAppDev/konsist",
    "category": "Kotlin",
    "last_reviewed": "2026-10-23",
    "sources": [
      "https://github.com/LemonAppDev/konsist",
      "https://repo1.maven.org/maven2/com/lemonappdev/konsist/maven-metadata.xml",
      "research/stack-go-rust-jvm-dotnet.md"
    ],
    "rationale": "Kotlin source-level architecture and convention rules as JUnit or Kotest tests. v0.18.1, 2026-10-10.",
    "limitations": "Pre-1.0; library inside the test suite; not run during this review."
  },
  {
    "id": "dotnet-sdk-analyzers",
    "repo": "dotnet/sdk",
    "category": ".NET",
    "last_reviewed": "2026-10-23",
    "sources": [
      "https://learn.microsoft.com/en-us/dotnet/core/project-sdk/msbuild-props",
      "https://learn.microsoft.com/en-us/nuget/concepts/auditing-packages",
      "research/stack-go-rust-jvm-dotnet.md"
    ],
    "rationale": "Built-in analyzers, code style in build, dotnet format and NuGet Audit (NU1903/NU1904 as errors) cover the baseline with no extra package. SDK v10.0.402.",
    "limitations": "Rule sets change with SDK versions; pin AnalysisLevel. Audit data from GitHub Advisory Database. dotnet format flags not re-read this review."
  },
  {
    "id": "meziantou-analyzer",
    "repo": "meziantou/Meziantou.Analyzer",
    "category": ".NET",
    "last_reviewed": "2026-10-23",
    "sources": [
      "https://github.com/meziantou/Meziantou.Analyzer",
      "https://www.nuget.org/packages/Meziantou.Analyzer",
      "research/stack-go-rust-jvm-dotnet.md"
    ],
    "rationale": "MIT-licensed Roslyn analyzer for API design, performance and usage; documents overlap with other analyzers. 3.0.316, 2026-10-21. SonarAnalyzer (source-available licence), StyleCop (betas only) and Security Code Scan (stale) not chosen.",
    "limitations": "Opinionated; tune severity in .editorconfig. Roslynator (Apache-2.0, 5.0.1) is a comparable alternative not compared rule by rule."
  },
  {
    "id": "archunitnet",
    "repo": "TNG/ArchUnitNET",
    "category": ".NET",
    "last_reviewed": "2026-10-23",
    "sources": [
      "https://github.com/TNG/ArchUnitNET",
      "https://www.nuget.org/packages/TngTech.ArchUnitNET",
      "research/stack-go-rust-jvm-dotnet.md"
    ],
    "rationale": "Active architecture-test library for C#; NetArchTest has had no release since 2021.",
    "limitations": "Pre-1.0 (0.13.4). NuGet lists a 2.1.0-draft version that was not investigated."
  },
  {
    "id": "credo",
    "repo": "rrrene/credo",
    "category": "Elixir",
    "last_reviewed": "2026-10-23",
    "sources": ["https://hex.pm/packages/credo", "https://github.com/rrrene/credo", "research/stack-go-rust-jvm-dotnet.md"],
    "rationale": "The mainstream Elixir static analyser with custom checks. 1.7.19, 2026-06-25.",
    "limitations": "Strict mode, JSON output and exit codes not verified in docs this review. Style-level only; no type checking."
  },
  {
    "id": "sobelow",
    "repo": "sobelow/sobelow",
    "category": "Elixir",
    "last_reviewed": "2026-10-23",
    "sources": ["https://hex.pm/packages/sobelow", "https://github.com/sobelow/sobelow", "research/stack-go-rust-jvm-dotnet.md"],
    "rationale": "Phoenix security scanner with --exit threshold and JSON output. 0.16.0, 2026-09-30. The old nccgroup/sobelow repository is stale.",
    "limitations": "Phoenix only. Organisation repo created 2025-05; moved from nccgroup/sobelow."
  },
  {
    "id": "dialyxir",
    "repo": "jeremyjh/dialyxir",
    "category": "Elixir",
    "last_reviewed": "2026-10-23",
    "sources": ["https://hex.pm/packages/dialyxir", "https://github.com/jeremyjh/dialyxir", "research/stack-go-rust-jvm-dotnet.md"],
    "rationale": "Dialyzer wrapper with exit status, ignore files and unused-filter check for CI. 1.4.8, 2026-09-05.",
    "limitations": "Success typing finds only definite errors. Slow PLT build on a cold cache. Effect of newer Elixir type work not checked."
  },
  {
    "id": "swiftlint",
    "repo": "realm/SwiftLint",
    "category": "Swift",
    "last_reviewed": "2026-10-23",
    "sources": ["https://github.com/realm/SwiftLint", "research/stack-go-rust-jvm-dotnet.md"],
    "rationale": "Swift rules on SwiftSyntax with --strict, --fix, SARIF and other reporters, custom rules. 0.65.1, 2026-08-21.",
    "limitations": "Linter, not formatter. Formatter choice (swift-format vs SwiftFormat) has no clear winner and is not proposed."
  }
]
```

Registry note: `category` values (Java, Kotlin, .NET, Elixir, Swift) are new and need matching README headings. `check-registry.mjs` was not run (I was told not to modify the repo; the JSON above was not validated against its schema).

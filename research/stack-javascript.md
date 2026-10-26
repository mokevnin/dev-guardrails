# JavaScript / TypeScript stack research

Reviewed 2026-10-23. Data: `gh api repos/...`, `npm view`, official docs fetched with WebFetch (summaries produced by a small model, so figures quoted from docs are "per docs", not re-counted), and small local runs (marked **ran**). "Last push" is `pushed_at`; "last release" is the latest GitHub release or npm publish date.

Stars and dates are a snapshot. Anything marked *unverified* was not checked.

## Cross-cutting findings

- **TypeScript 7 is the native compiler and is stable.** `typescript@7.0.2` is on npm (modified 2026-10-23), and `tsc --version` printed 7.0.2 (**ran**). `microsoft/typescript-go` is **archived (2026-08-31 push) because the port finished**, not abandoned; development continues in `microsoft/TypeScript`. The compiler API is "not ready" per the repo README.
- **typescript-eslint does not support TS 7 yet.** Its latest (8.72.0) declares peer `typescript >=4.8.4 <6.1.0` (npm). Issue #10940 "Use TS 7 (tsgo) for type information" is open. Consequence: type-aware ESLint rules need TS 6.0.x installed for linting, while `tsc` for type checking can be 7. Conversely **Oxlint type-aware linting requires TS 7+** (per oxc docs). I did not test running both TS versions side by side.
- **ESLint 9 reached end of life on 2026-08-06** (per eslint.org blog). Current is v10.13.0.
- **Oxlint exits 0 on warnings by default** (**ran**: findings printed as warnings, exit 0). CI needs `--deny-warnings` or `-D <category>` (**ran**: both exit 1). With `--type-aware`, rules enabled via `-D` become errors as expected.
- **Vite+ 1.0 (MIT, 2026-10-23 release v1.4.0, VoidZero, reported as acquired by Cloudflare)** bundles Vite, Vitest, Oxlint, Oxfmt, Rolldown and runs `vp check` (format + lint + type check). It is a toolchain/runner, not a new checker; it adds no rules of its own. Not proposed.
- **npm supply chain, 2026 (WebSearch, counts disputed between sources):** ChainDrop worm (Aug 2026, Keyv family, 444 to 868 packages depending on source, valid provenance because it published through legitimate workflows), Mastra (Jun 2026), Red Hat packages (Jun 2026), AsyncAPI (Jul 2026). None involved ESLint or Prettier. Provenance alone is not a safe signal. pnpm 11+ defaults `minimumReleaseAge` to 1440 minutes (per pnpm docs; added in 10.16, default since v11) and `blockExoticSubdeps` is true by default; `trustPolicy: no-downgrade` is off by default. These are package-manager settings, not a separate tool, so they belong in docs/patterns, not in the tool list.

## 1. Linting (JS/TS)

| Candidate | Last release | Last push | License | Stars |
|---|---|---|---|---|
| [eslint/eslint](https://github.com/eslint/eslint) | v10.13.0 (2026-10-16) | 2026-10-23 | MIT | 27.6k |
| [typescript-eslint](https://github.com/typescript-eslint/typescript-eslint) | v8.72.0 (2026-10-19) | 2026-10-23 | MIT | 16.4k |
| [biomejs/biome](https://github.com/biomejs/biome) | 2.6.2 (2026-10-21) | 2026-10-23 | Apache-2.0 (npm: MIT OR Apache-2.0) | 26.0k |
| [oxc-project/oxc](https://github.com/oxc-project/oxc) (Oxlint) | oxlint 1.89.0 (2026-10-19) | 2026-10-23 | MIT | 23.2k |
| [oxc-project/tsgolint](https://github.com/oxc-project/tsgolint) | v7.0.2005 (2026-10-22) | 2026-10-22 | MIT | 1.5k |

What each enforces (per docs unless marked **ran**):

- **ESLint 10 + typescript-eslint:** the only one with complete framework coverage (Vue, Svelte and Angular templates via their official parsers), stable custom-rule API, and the full plugin ecosystem. `--max-warnings 0`, JSON and other formatters, `--fix`. Slowest of the three. Peer-compat: eslint-plugin-vue, -svelte, @angular-eslint, react-hooks and typescript-eslint all declare ESLint 10 support (npm).
- **Oxlint:** about 871 rules (docs), type-aware via tsgolint (docs: 59 of 61 typescript-eslint type-aware rules; "rule coverage incomplete"; needs TS 7, no `baseUrl`), multi-file rules such as `import/no-cycle`, output formats include `agent`, `json`, `sarif`, `github`, `junit`, `gitlab` (docs). JS plugins are **alpha**; Vue/Svelte/Astro files are linted for `<script>` only; no template linting. Ran: `--type-aware` flagged `no-floating-promises` on a toy file.
- **Biome:** linter and formatter in one binary, over 500 lint rules (v2.5 post), 15 HTML a11y rules and better Vue/Svelte/Astro support (v2.4 post), Markdown/YAML/SCSS added in v2.6 (YAML has one rule). Custom rules via GritQL plugins; JS plugins are a **developer preview** (v2.6 post). Type inference is Biome's own engine, not the TS compiler; coverage versus typescript-eslint is quoted as 75 to 85 % by blog posts (not verified). Ran: `biome ci` prints diagnostics and fails on a toy file (exit code lost in my shell pipe; assumed non-zero because it printed "errors were emitted").

**Recommendation: ESLint 10 with typescript-eslint as the default.** It covers the most checks across frameworks and allows stable custom rules, which the selection criteria weight. It is not the fastest. **Oxlint is a legitimate second tier** for speed-critical or very large repos without Vue/Svelte/Angular template needs and with TS 7; run it with `--deny-warnings`. Do not run Oxlint and ESLint over the same rules; `eslint-plugin-oxlint` exists to disable the overlap (npm 1.89.0). **No clear winner** between ESLint and Oxlint in general; the choice depends on framework and on TS 6 vs 7 pinning.
Limits: slow on large repos; type-aware ESLint ties you to TS 6.x until typescript-eslint supports TS 7.
Confidence: **medium**. Not verified: real speed (only blog benchmarks that disagree), Oxlint rule counts, Biome exit codes and SARIF output, Biome type-aware coverage.

### Framework plugins (all ESLint)

| Plugin | Last release | License | Notes |
|---|---|---|---|
| [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) | v7.37.5 (2025-04-03) | MIT | Peer `eslint ^9.7` max; commits continue (push 2026-10-23), open PRs for ESLint 10. |
| [eslint-plugin-react-hooks](https://www.npmjs.com/package/eslint-plugin-react-hooks) | 7.1.1 (npm 2026-10-23) | MIT | Peer includes ESLint 10. |
| [@eslint-react/eslint-plugin](https://www.npmjs.com/package/@eslint-react/eslint-plugin) | 5.28.8 (2026-10-23) | MIT | Active alternative; not compared on rule coverage. |
| [eslint-plugin-vue](https://github.com/vuejs/eslint-plugin-vue) | v10.11.1 (2026-09-24) | MIT | Peer ESLint 10 ok. |
| [eslint-plugin-svelte](https://github.com/sveltejs/eslint-plugin-svelte) | 3.23.1 (2026-10-09) | MIT | Peer ESLint 10 ok. |
| [angular-eslint](https://github.com/angular-eslint/angular-eslint) | v22.6.0 (2026-10-11) | MIT | Peer ESLint 9 or 10. |
| [eslint-config-next](https://github.com/vercel/next.js) | 16.4.3 (2026-10-23) | MIT | Peer `eslint >=9`. |

Recommendation: use the official plugin of each framework; no ranking needed. Not proposed as README entries (they are configuration of the ESLint entry). Risk: eslint-plugin-react and eslint-plugin-jsx-a11y have had no release for 12 to 21 months and do not declare ESLint 10 in peers.

## 2. Formatting

| Candidate | Last release | Last push | License | Stars |
|---|---|---|---|---|
| [prettier/prettier](https://github.com/prettier/prettier) | 3.9.10 (2026-10-10) | 2026-10-23 | MIT | 52.4k |
| oxfmt (in [oxc](https://github.com/oxc-project/oxc)) | oxfmt 0.74.0 (2026-10-19) | 2026-10-23 | MIT | (shared) |
| Biome formatter | 2.6.2 | 2026-10-23 | Apache-2.0 | (shared) |
| [dprint/dprint](https://github.com/dprint/dprint) | 0.64.3 (2026-10-23) | 2026-10-23 | MIT | 4.1k |

- **Prettier** is the reference output; supports every web language and has the most plugins. Slower.
- **oxfmt** is still 0.x (0.74.0). Docs say it uses Prettier output as baseline and is tested against Prettier's test suite; it covers JS/TS, JSON, YAML, TOML, HTML, Vue, Svelte, CSS/SCSS/Less, Markdown, MDX and GraphQL, with built-in import sorting, Tailwind class sorting and package.json sorting (docs; I did not confirm which are native Rust vs delegated). Ran: `oxfmt --check` exit 1 on an unformatted file.
- **Biome** formats fewer languages than Prettier and deliberately differs in details.
- **dprint** is fast and plugin-based but is a smaller ecosystem; no reason to prefer it.

**Recommendation: Prettier.** Maximum language coverage and reference behaviour; `prettier --check` exits non-zero. Re-review oxfmt when it reaches 1.0 or publishes a Prettier conformance figure. Limits: slower; formatting only (do not use ESLint style rules alongside it).
Confidence: **medium**. Not verified: oxfmt conformance percentage, Prettier timing.

## 3. Type checking

| Candidate | Last release | Last push | License | Stars |
|---|---|---|---|---|
| [microsoft/TypeScript](https://github.com/microsoft/TypeScript) (`tsc`, v7 native) | npm 7.0.2 (2026-10-23); GitHub v7.0.2 (2026-08-20) | 2026-10-23 | Apache-2.0 | 111.6k |
| [microsoft/typescript-go](https://github.com/microsoft/typescript-go) | typescript/v7.0.2 (2026-07-08) | **archived**, 2026-08-31 | Apache-2.0 | 26.1k |
| `@typescript/native-preview` (`tsgo`) | 7.0.0-dev.20260707.2 | n/a | Apache-2.0 | n/a |

Recommendation: **`tsc --noEmit` from `typescript@7`** with `strict` on. Skip `@typescript/native-preview`: superseded by 7.0 and last published July 2026. README says type errors match TS 6.0; declaration emit differs on purpose. Limits: compiler API not ready, so tools that import `typescript` (typescript-eslint, some Knip/plugins, ts-morph-style scripts) may need TS 6 beside it. Confidence: **high** for the tool, **medium** for the TS 6 + TS 7 coexistence advice (not tested).

## 4. Unused code and dependencies

[Knip](https://github.com/webpro-nl/knip) is already recommended: knip@6.42.1 (2026-10-19), push 2026-10-23, ISC, 12.5k stars. Nothing newer found. Not re-compared. Confidence: high.

### React Doctor (reviewed 2026-10-26)

[millionco/react-doctor](https://github.com/millionco/react-doctor): react-doctor 0.9.18 (2026-10-12), push 2026-10-26, 15.0k stars, 406 open issues, not archived (`gh api`, `npm view`). **Licence is not plain MIT:** GitHub reports `NOASSERTION`, npm says "SEE LICENSE IN LICENSE", and the file is a "Modified MIT" that needs written permission to use the software as AI training or evaluation data or to offer it as a paid hosted product. The README says "MIT-licensed". Ordinary CI use is allowed; the clause matters if you build tooling on it.

What I **ran** (0.9.18, `research/fixtures/react-doctor/run.py`): a two-file app flagged 7 findings (derived state, `dangerouslySetInnerHTML` with children, index keys, click handler without keyboard handler, and others). With an error present it exits 1. With warnings only: exit 0 by default, 1 with `--blocking warning`, 0 with `--blocking none`, 3 with `--warning-exit-code 3`. `--json` gives a structured report (schema version 3), `--scope changed` and `--baseline` report only new issues, `--staged` fits a pre-commit hook. So it can fail a build.

Read, not run: the 0-100 score comes from a remote score API and the supply-chain scan uses Socket.dev; `--no-telemetry` (alias of `--no-score`) turns the score off. Dead-code detection claimed by third-party listings: **not verified** (an unused file in the fixture was not reported in the text output).

Overlap: its lint rules sit on Oxlint, and the hooks, a11y and key rules duplicate eslint-plugin-react-hooks, jsx-a11y and eslint-plugin-react. Dead code overlaps Knip. It also ships `eslint-plugin-react-doctor` and `oxlint-plugin-react-doctor` 0.9.18, so the rules can run inside the recommended linter instead of a second CLI.

Verdict: **not added as a README entry.** Reason: overlap with the lint entry and Knip, a non-standard licence, and a score that depends on a remote service. Worth a second look: the React-specific rules (derived state, effects, rerender) that eslint-plugin-react lacks, via its ESLint or Oxlint plugin. Confidence: medium; I did not compare rule coverage against `@eslint-react/eslint-plugin` or measure speed.

## 5. Architecture and import boundaries

| Candidate | Last release | Last push | License | Stars |
|---|---|---|---|---|
| [sverweij/dependency-cruiser](https://github.com/sverweij/dependency-cruiser) | v18.7.0 (2026-10-19) | 2026-10-23 | MIT | 7.3k |
| [javierbrea/eslint-plugin-boundaries](https://github.com/javierbrea/eslint-plugin-boundaries) | v7.3.0 (2026-10-23) | 2026-10-23 | MIT | 1.0k |
| [sheriff-arch/sheriff](https://github.com/sheriff-arch/sheriff) (formerly softarc-consulting) | v0.20.0 (2026-10-07) | 2026-09-29 | MIT | 325 |
| `@nx/enforce-module-boundaries` in [nrwl/nx](https://github.com/nrwl/nx) | 24.0.1 (2026-10-23) | 2026-10-23 | MIT | 29.4k |

- **dependency-cruiser:** whole-graph rules in a config file: forbidden paths, circular, orphans, dev-dep use, unresolvable imports. Ran: a circular import produced `error no-circular` with exit 1; `--output-type json` works; `--ignore-known` (baseline) and `--metrics` exist in `--help`. Node `^22||^24||>=26`. No autofix (not applicable).
- **eslint-plugin-boundaries:** element-type rules inside ESLint, so violations show in the editor; JS/TS only through ESLint; peer `eslint >=6`.
- **Sheriff:** tag-based modules with index.ts public APIs, CLI or ESLint plugin; pre-1.0 and small.
- **Nx:** needs Nx project graph; only worthwhile if you already use Nx.

**Recommendation: dependency-cruiser.** Independent of the lint stack, works with any bundler or monorepo, machine-readable output, baseline for adoption on legacy code. Use eslint-plugin-boundaries instead only if you want editor feedback and already run ESLint (they overlap; do not run both). Limits: static resolution misses dynamic imports; large repos need `--cache` and a tuned `tsconfig`. Confidence: **medium-high**. Not verified: performance on large monorepos; Sheriff and boundaries feature depth beyond READMEs.

## 6. Package hygiene

| Candidate | Last release | Last push | License | Stars |
|---|---|---|---|---|
| [publint/publint](https://github.com/publint/publint) | 0.3.25 (2026-10-01) | 2026-10-01 | MIT | 1.3k |
| [arethetypeswrong](https://github.com/arethetypeswrong/arethetypeswrong.github.io) | cli 0.18.5 npm (2026-07-09) | 2026-07-09 | MIT | 1.6k |
| [ai/size-limit](https://github.com/ai/size-limit) | 14.3.0 (2026-10-22) | 2026-10-22 | MIT | 7.0k |
| [JamieMason/syncpack](https://github.com/JamieMason/syncpack) | 15.3.3 (2026-08-09) | 2026-10-13 | MIT | 2.1k |
| [QuiiBz/sherif](https://github.com/QuiiBz/sherif) | v1.13.0 (2026-07-04) | 2026-07-04 | MIT | 1.2k |
| [lirantal/lockfile-lint](https://github.com/lirantal/lockfile-lint) | 5.1.0 npm (2026-10-09) | 2026-10-09 | Apache-2.0 | 870 |

- **publint** checks `package.json` exports, main, module, files against the packed tarball (**ran**: `publint` packed and linted a toy package; it emitted "Suggestions" and exit 0, so use its strict flag in CI; flag name not verified). **attw** checks type resolution in node10, node16 and bundler modes (12 problem classes per README). They overlap only in part: publint = package metadata, attw = types. Both matter only for **published libraries**.
- **size-limit:** fails CI when real bundle cost (size or time) exceeds a budget; has a GitHub Action. Library or app budget; needs a bundler plugin.
- **syncpack vs Sherif:** syncpack covers version-consistency policy, pinned/banned deps, semver range rules, catalogs and package.json sorting, lint plus fix; Sherif is zero-config, Rust, fewer rules, last release July 2026. pnpm/bun catalogs reduce the need for either. **Recommend syncpack** for monorepos that do not use catalogs everywhere; Sherif is the zero-config alternative (no clear winner for small monorepos).
- **lockfile-lint** validates registry hosts and integrity in lockfiles; not compared against alternatives, **not proposed**.

Recommendations: publint, arethetypeswrong (libraries only), size-limit (when bundle size is a requirement), syncpack (monorepos). Confidence: **medium**. Not verified: arethetypeswrong CLI exit code and flags (docs not read), syncpack v15 exit codes, size-limit behaviour (README only).

## 7. CSS

| Candidate | Last release | Last push | License | Stars |
|---|---|---|---|---|
| [stylelint/stylelint](https://github.com/stylelint/stylelint) | 17.16.0 (2026-10-01) | 2026-10-23 | MIT | 11.5k |
| Biome CSS lint | 2.6.2 | 2026-10-23 | Apache-2.0 | (shared) |
| [@eslint/css](https://www.npmjs.com/package/@eslint/css) | 2.0.1 (2026-10-15) | n/a | Apache-2.0 | n/a |

**Recommendation: Stylelint.** Large rule set, plugins, autofix, custom rules. Biome's CSS rules are a subset (its own post says SCSS rules cannot yet handle loops and mixins); `@eslint/css` is a small rule set. Limits: do not enable formatting rules next to Prettier (Stylelint 15+ dropped them; verify in your config version). Confidence: **medium**. Not verified: rule counts of Biome CSS and @eslint/css.

## 8. HTML and accessibility

| Candidate | Last release | Last push | License | Stars |
|---|---|---|---|---|
| [dequelabs/axe-core](https://github.com/dequelabs/axe-core) (+ `@axe-core/playwright` 4.14.0, `@axe-core/cli` 4.14.0) | v4.14.0 (2026-10-05) | 2026-10-22 | MPL-2.0 | 7.7k |
| [jsx-eslint/eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) | v6.10.2 (2025-01-05) | 2026-01-06 | MIT | 3.6k |
| [html-validate](https://github.com/html-validate/html-validate) (GitHub is a mirror of GitLab) | 11.17.0 npm (2026-10-20) | 2026-10-23 | MIT | 19 (mirror) |
| [@html-eslint/eslint-plugin](https://github.com/yeonjuan/html-eslint) | 0.67.0 npm (2026-10-14) | 2026-10-23 | MIT | 275 |
| [pa11y/pa11y](https://github.com/pa11y/pa11y) | 10.0.0 (2026-08-28) | 2026-10-19 | LGPL-3.0 | 4.6k |

- **axe-core** tests rendered DOM against WCAG 2.0/2.1/2.2 A, AA, AAA and best practices; "finds 57 % of WCAG issues on average" per the project (vendor claim, unverified); flags "incomplete" items for manual review. CI use: call `axe.run()` or `@axe-core/playwright` in tests and fail when `violations` is non-empty. This is a test integration, not a standalone CLI gate.
- **eslint-plugin-jsx-a11y:** static JSX checks. Stale release (Jan 2025), peer `eslint <=9`. **Ran:** with `--legacy-peer-deps` on ESLint 10.13.0 the `alt-text` rule fired and exit was non-zero, so it works for at least that rule; other rules not tested. Open ESLint 10 PRs exist. Oxlint and Biome ship jsx-a11y style rules natively (Oxlint docs list jsx-a11y; Biome has a11y rules) as the alternative.
- **html-validate:** offline HTML5 validator for templates and fragments; primary repo is on GitLab, GitHub is a mirror. Alternative to `@html-eslint` (rules inside ESLint). Not compared on rules.
- **pa11y:** LGPL-3.0, wraps HTML_CodeSniffer/axe; overlaps axe, not preferred.

**Recommendation: axe-core via `@axe-core/playwright`** for rendered pages (a11y problems visible only at runtime). For static JSX use the jsx-a11y rules (inside the ESLint entry) with the caveat above. No recommendation for html-validate vs @html-eslint (**no clear winner**, low confidence). Limits: automated checks cover only part of WCAG; MPL-2.0. Confidence: **medium** for axe, **low** for static HTML. Not verified: axe CLI behaviour, html-validate exit codes.

## 9. Test enforcement (coverage)

[vitest-dev/vitest](https://github.com/vitest-dev/vitest) v5.0.5 (2026-10-15), push 2026-10-23, MIT, 17.3k stars; `@vitest/coverage-v8` 5.0.5. Docs: `coverage.thresholds` with `lines|functions|branches|statements`, `perFile`, per-glob thresholds, negative numbers as max uncovered, `autoUpdate`. **The docs page does not state the exit code**, and my local run failed on a module-resolution error unrelated to coverage (possibly a full disk), so the non-zero exit is **unverified by me**. It is a feature of the test runner, not a separate tool; a separate coverage entry would not fit the one-job-per-tool rule. Not proposed. Do not enable `autoUpdate` unattended (it loosens nothing but ratchets silently and rewrites config). Jest, c8, nyc not compared.

## 10. Monorepo constraints

[Nx](https://github.com/nrwl/nx) 24.0.1 and [Turborepo](https://github.com/vercel/turborepo) v2.11.10 (2026-10-20, MIT, 31.2k stars) are task runners. Nx enforces boundaries with `@nx/enforce-module-boundaries`; Turborepo has `turbo boundaries` (existence from memory, **not verified here**). Use dependency-cruiser for boundaries when you want a runner-independent rule, and syncpack/Sherif for versions. Not proposed.

## Newer tools that might replace several

- **Biome v2.6** replaces ESLint + Prettier on a single binary and is the only candidate with this reach; it loses on framework template coverage, type-aware rules and stable custom rules (JS plugins are a preview). Considered, not chosen as the default, but a defensible choice for small TS/React/Node projects. Re-review when JS plugins leave preview.
- **Oxlint + Oxfmt + tsgolint** (and Vite+ as the wrapper): fastest toolchain; blocked from default by JS plugin alpha, no template linting and oxfmt 0.x.
- **@e18e/eslint-plugin** 0.8.1 (2026-09-17): ESLint rules for modern dependency replacement ("modernization"); small and pre-1.0; not proposed. Also listed by Oxlint docs as working through JS plugins.
- No tool found that replaces dependency-cruiser + knip + syncpack together.

## Proposed README entries

Only the first four are strong enough to ship now. The rest are conditional; add them one pull request each per CONTRIBUTING.md.

```markdown
- **[ESLint](https://github.com/eslint/eslint)**: linter for JavaScript, TypeScript, JSX, Vue, Svelte and Angular with `--fix`, JSON/SARIF-capable formatters, `--max-warnings 0` and stable custom rules; use typescript-eslint for type-aware rules. Chosen because no faster tool covers framework templates and custom rules as completely. *Limits:* slow on large repos; typescript-eslint does not support TypeScript 7 yet, so type-aware linting needs TypeScript 6.x. For speed-first repos without template linting see [Oxlint](https://github.com/oxc-project/oxc) (exits 0 on warnings unless `--deny-warnings`). [Details](research/stack-javascript.md).
- **[Prettier](https://github.com/prettier/prettier)**: formatting for JS, TS, CSS, Markdown, JSON, YAML and more; `prettier --check` fails CI. Chosen as the reference output with the widest language coverage. *Limits:* slower than oxfmt and Biome; oxfmt is 0.x and kept as a candidate to re-review.
- **[TypeScript](https://github.com/microsoft/TypeScript)**: `tsc --noEmit` with `strict`; version 7 is the native, much faster compiler. *Limits:* the TypeScript 7 compiler API is not ready, so tools that import `typescript` may need TypeScript 6 beside it. `microsoft/typescript-go` is archived because it was merged, not abandoned.
- **[dependency-cruiser](https://github.com/sverweij/dependency-cruiser)**: import-graph rules (forbidden paths, cycles, orphans, dev-deps in production code) with non-zero exit and JSON output; `--ignore-known` baselines legacy violations. Chosen over eslint-plugin-boundaries because it does not depend on the lint stack. *Limits:* static analysis misses dynamic imports; no autofix.
- **[publint](https://github.com/publint/publint)**: packaging errors in `package.json` exports, main and files of a published library. *Limits:* libraries only; check the strict flag for CI exit behaviour.
- **[arethetypeswrong](https://github.com/arethetypeswrong/arethetypeswrong.github.io)**: wrong or missing types for a published library under node10, node16 and bundler resolution. *Limits:* libraries only; overlaps publint only in part.
- **[size-limit](https://github.com/ai/size-limit)**: fails CI when bundle cost (size or load time) exceeds a budget. *Limits:* needs a bundler plugin; only useful when bundle size is a requirement.
- **[syncpack](https://github.com/JamieMason/syncpack)**: one dependency version across a monorepo, banned and pinned dependencies, semver range policy, with fix. *Limits:* less needed where pnpm or bun catalogs are used; [Sherif](https://github.com/QuiiBz/sherif) is the zero-config alternative.
- **[Stylelint](https://github.com/stylelint/stylelint)**: CSS, SCSS and CSS-in-JS rules with autofix and plugins. Chosen over Biome's CSS rules for rule breadth. *Limits:* leave formatting to Prettier.
- **[axe-core](https://github.com/dequelabs/axe-core)**: accessibility violations on a rendered page, via `@axe-core/playwright` in tests. *Limits:* finds only part of WCAG issues (vendor claim: 57 %); MPL-2.0; a test integration, not a standalone gate.
```

```json
[
  {
    "id": "eslint",
    "repo": "eslint/eslint",
    "category": "JavaScript and TypeScript",
    "last_reviewed": "2026-10-23",
    "sources": ["https://eslint.org/blog/", "https://typescript-eslint.io/", "https://oxc.rs/docs/guide/usage/linter.html", "https://biomejs.dev/blog/biome-v2-6/", "research/stack-javascript.md"],
    "rationale": "Widest rule and framework coverage (Vue, Svelte, Angular, React) with stable custom rules, --fix and --max-warnings 0. v10.13.0, MIT. Compared with Oxlint (faster, template files not linted, JS plugins alpha) and Biome (one binary with formatter, JS plugins in developer preview).",
    "limitations": "Slow on large repos. typescript-eslint 8.72.0 declares typescript <6.1.0 and does not support TypeScript 7. Oxlint is a valid fast tier for repos without template linting; it exits 0 on warnings unless --deny-warnings."
  },
  {
    "id": "prettier",
    "repo": "prettier/prettier",
    "category": "JavaScript and TypeScript",
    "last_reviewed": "2026-10-23",
    "sources": ["https://prettier.io/docs/", "https://oxc.rs/docs/guide/usage/formatter.html", "research/stack-javascript.md"],
    "rationale": "Reference formatter with the widest language coverage; --check exits non-zero. 3.9.10, MIT. Compared with oxfmt (0.74.0, pre-1.0), Biome and dprint.",
    "limitations": "Slower than Rust formatters. oxfmt to be re-reviewed at 1.0."
  },
  {
    "id": "typescript",
    "repo": "microsoft/TypeScript",
    "category": "JavaScript and TypeScript",
    "last_reviewed": "2026-10-23",
    "sources": ["https://github.com/microsoft/typescript-go", "https://www.npmjs.com/package/typescript", "research/stack-javascript.md"],
    "rationale": "tsc 7.0.2 is the native compiler; type errors match TS 6.0 per the typescript-go README. microsoft/typescript-go is archived because the port finished and merged into this repo.",
    "limitations": "Compiler API not ready; typescript-eslint requires typescript <6.1.0, so lint tooling may need TypeScript 6 beside it. Versioned through npm."
  },
  {
    "id": "dependency-cruiser",
    "repo": "sverweij/dependency-cruiser",
    "category": "Architecture (JS/TS)",
    "last_reviewed": "2026-10-23",
    "sources": ["https://github.com/sverweij/dependency-cruiser/blob/main/doc/rules-reference.md", "research/stack-javascript.md"],
    "rationale": "Graph-level import rules with non-zero exit and JSON output, independent of the linter. v18.7.0, MIT. Compared with eslint-plugin-boundaries, Sheriff (0.20.0) and Nx enforce-module-boundaries. Verified locally that a circular import fails with exit 1.",
    "limitations": "Static analysis misses dynamic imports. Node ^22, ^24 or >=26. No autofix."
  },
  {
    "id": "publint",
    "repo": "publint/publint",
    "category": "Package hygiene (JS/TS)",
    "last_reviewed": "2026-10-23",
    "sources": ["https://publint.dev/", "research/stack-javascript.md"],
    "rationale": "Checks package.json exports, main and files against the packed tarball. 0.3.25, MIT.",
    "limitations": "Libraries only. Default run printed suggestions and exited 0 in a local test; confirm the strict flag for CI."
  },
  {
    "id": "arethetypeswrong",
    "repo": "arethetypeswrong/arethetypeswrong.github.io",
    "category": "Package hygiene (JS/TS)",
    "last_reviewed": "2026-10-23",
    "sources": ["https://github.com/arethetypeswrong/arethetypeswrong.github.io", "research/stack-javascript.md"],
    "rationale": "Detects wrong or missing types for published packages under node10, node16 and bundler resolution; complementary to publint. CLI 0.18.5, MIT.",
    "limitations": "Libraries only. Last push 2026-07-09; CLI exit code and flags not verified."
  },
  {
    "id": "size-limit",
    "repo": "ai/size-limit",
    "category": "Package hygiene (JS/TS)",
    "last_reviewed": "2026-10-23",
    "sources": ["https://github.com/ai/size-limit", "research/stack-javascript.md"],
    "rationale": "Performance budget: fails CI when real bundle size or load time exceeds the limit. 14.3.0, MIT.",
    "limitations": "Needs a bundler plugin. Useful only where bundle size is a requirement."
  },
  {
    "id": "syncpack",
    "repo": "JamieMason/syncpack",
    "category": "Package hygiene (JS/TS)",
    "last_reviewed": "2026-10-23",
    "sources": ["https://syncpack.dev/", "https://github.com/QuiiBz/sherif", "research/stack-javascript.md"],
    "rationale": "Version consistency, banned and pinned dependencies, semver range policy, catalogs; lint and fix. 15.3.3, MIT. Compared with Sherif (zero-config, fewer rules).",
    "limitations": "Less needed with pnpm or bun catalogs. Exit codes not verified locally."
  },
  {
    "id": "stylelint",
    "repo": "stylelint/stylelint",
    "category": "CSS",
    "last_reviewed": "2026-10-23",
    "sources": ["https://stylelint.io/", "https://biomejs.dev/blog/biome-v2-6/", "research/stack-javascript.md"],
    "rationale": "Broadest CSS and SCSS rule set with autofix and plugins. 17.16.0, MIT. Compared with Biome CSS rules and @eslint/css (both smaller).",
    "limitations": "Leave formatting to Prettier. Rule counts of the alternatives not verified."
  },
  {
    "id": "axe-core",
    "repo": "dequelabs/axe-core",
    "category": "Accessibility",
    "last_reviewed": "2026-10-23",
    "sources": ["https://github.com/dequelabs/axe-core", "https://www.npmjs.com/package/@axe-core/playwright", "research/stack-javascript.md"],
    "rationale": "Runtime WCAG 2.0 to 2.2 checks on rendered DOM, run in tests through @axe-core/playwright. v4.14.0, MPL-2.0. Compared with pa11y (LGPL-3.0, overlapping) and static linters.",
    "limitations": "Vendor claim of 57 percent of WCAG issues found; the rest needs manual review. A test integration, not a standalone CLI gate."
  }
]
```

## Not verified, summarised

- Real-world speed of ESLint vs Oxlint vs Biome (only third-party blog numbers, which disagree).
- Biome and arethetypeswrong exit codes and machine-readable output; syncpack and publint strict-mode exit codes.
- Vitest coverage-threshold exit code (docs silent; my run failed for an unrelated reason).
- TS 6 plus TS 7 coexistence for typescript-eslint; Turborepo `boundaries`.
- Oxfmt conformance percentage and which languages are native.
- Whether eslint-plugin-jsx-a11y and eslint-plugin-react work fully on ESLint 10 (one rule each tested; install needed `--legacy-peer-deps`).
- html-validate vs @html-eslint rule coverage; Sheriff and eslint-plugin-boundaries depth.
- Doc claims quoted from WebFetch summaries (rule counts, 59 of 61 type-aware rules, 57 % WCAG).

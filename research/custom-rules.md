# Custom rules and architecture as code

Date: 2026-10-25. Claims marked **ran** were run with ast-grep 0.51.0 or archspec 1.1.0 (Ruby 4.0.9) on 2026-10-25; the ast-grep ones are reproduced by [`fixtures/ast-grep/run.py`](fixtures/ast-grep/run.py). Claims marked **read** come from documentation only.

Conclusion: keep ast-grep as the one tool for project-specific syntax rules, and add archspec as the Ruby architecture option. The other architecture-as-code libraries are recorded in [not-adopted](../docs/not-adopted.md) because each overlaps a tool we already list.

## ast-grep

ast-grep matches code by syntax tree, not by text, using tree-sitter grammars (about 20 languages built in). A rule says what the code looks like; the same rule can report and rewrite it. It is one native binary, so it needs no runtime and runs in a pre-commit hook in well under a second on a typical repository.

### Layout

```text
sgconfig.yml          # ruleDirs and testConfigs
rules/*.yml           # one rule per file
rule-tests/*.yml      # valid / invalid snippets per rule
rule-tests/__snapshots__/
```

`sgconfig.yml` is two lines: `ruleDirs: [rules]` and `testConfigs: [{testDir: rule-tests}]`. `ast-grep scan` finds it by walking up from the working directory.

### What a rule can say

- **`pattern`**: code with metavariables: `console.log($$$ARGS)` matches any call; `$A` is one node, `$$$ARGS` is any number.
- **Relational rules**: `inside`, `has`, `follows`, `precedes`, each with `stopBy` to say how far to look. For example "a `console.log` that is not inside a `catch_clause`".
- **Composite rules**: `all`, `any`, `not`, `matches` (reuse another rule by id, with shared `utils`).
- **`kind` and `regex`**: match a tree-sitter node type, or the text of a node. `kind: import_statement` with a child `regex: /ui/` is an import-boundary rule.
- **`constraints`**: restrict what a metavariable may match.
- **`files` and `ignores`**: limit a rule to paths, so the same rule set can have different rules for `src/domain/**` and `src/ui/**`.
- **`fix` and `transform`**: rewrite the match, reusing metavariables; `transform` can change case, take substrings and replace text.
- **`severity`**: `error`, `warning`, `info`, `hint` or `off`; `message` and `note` carry the explanation an agent or reviewer sees.

Rules can also be passed inline (`ast-grep scan --inline-rules`) and a single pattern can be searched without any file (`ast-grep run -p 'PATTERN' -l ts`).

### Enforcement behaviour

| Claim | Evidence |
|---|---|
| `scan` exits 0 when only `warning` rules match; the findings are printed but do not fail the build. | **ran**, exit 0 |
| `scan` exits 1 when an `error` rule matches. | **ran**, exit 1 |
| `--format sarif` writes SARIF 2.1 with `error` and `warning` levels, for GitHub code scanning. | **ran**; `--json` also exists (**read**) |
| `ast-grep test` fails with exit 4 on a missing or stale snapshot, so a rule change must be reviewed. | **ran**, exit 4 both cases |
| `ast-grep test --update-all` rewrites snapshots. | **ran** |
| `--update-all` on `scan` applies `fix` to files. | **read** |

Practical consequence: give rules that must block a merge `severity: error`. A rule left at the default `hint` or at `warning` never fails CI, which is the most common mistake.

### Testing rules

A test file lists `valid` and `invalid` snippets for a rule id. The first `ast-grep test` has no baseline and fails; `--update-all` writes `__snapshots__/<rule>-snapshot.yml` with the matched span and the `fix` output. After that, any change to the rule that alters a match or a fix fails the test until the snapshot is updated in the same pull request. This is the main reason to prefer ast-grep for rules written by agents: the rule is checked against examples before it is trusted.

### Limits

- **One file at a time.** No cross-file resolution, so it cannot say "this import resolves to the UI package", only "this import string contains `/ui/`". Use dependency-cruiser, import-linter, ArchUnit or archspec for real dependency graphs.
- **No types and no data flow.** It cannot know a variable's type or follow a value. Use Opengrep for source-to-sink rules.
- **Pattern rules can over-match** on code that uses the same names; add `inside`, `kind` or `constraints` and put the valid case in the rule test.
- **Rewrites are syntactic.** Review `fix` output before using `--update-all` on a codebase.

### When to write a rule

Write one when a review comment repeats, a past incident has a recognisable code shape, or a library has a banned call. Keep the rule next to a test of both a violation and a safe case, and give it `severity: error` once the existing code is clean.

## Architecture rules as code: Ruby

| Tool | Stars | Latest release | Downloads | Notes |
|---|---|---|---|---|
| [archspec](https://github.com/crmne/archspec) | 262 | v1.1.0, 2026-08-27 | 199k gem | Created 2026-06-02, MIT, one maintainer |
| [Packwerk](https://github.com/Shopify/packwerk) | 1.9k | 3.3.1, 2026-08-26 | 23M gem | Package boundaries and privacy |

**ran** (archspec 1.1.0 on a two-file app with `models.cannot_use :controllers`): `archspec check` prints the violation with a code frame and exits 1; `archspec check --format json` returns violations with rule id, path, line and evidence. No SARIF output was found. Other claims below are **read** from its README.

What archspec adds over Packwerk: rules by layer and by constant, inheritance and mixins, named method calls (`cannot_call :render`), naming conventions, cycles, and Rails presets (`:rails`, `:vanilla_rails`, `:layered`, `:hexagonal`, `:modular_monolith`, `:cqrs`). It does not need the app split into packages. It also has a todo file for adopting it in an existing app (`--update-todo`, `--check-todo`) and inline suppressions that need a reason.

Overlap: its `modular_monolith` preset with a public API does the job of Packwerk. Use one of them for package boundaries. If the app is already modularised with `package.yml` files, keep Packwerk; if it is a plain Rails app with layers, start with archspec.

Limits: four months old, one maintainer, Ruby 3.2 or newer, depends on the Rubydex gem (installed as a native gem here), and checking is static, so dynamic dispatch is reported as unresolved in the analysis summary rather than checked.

Decision: **add** to the Ruby section, scoped to apps that are not already on Packwerk.

## Other architecture-as-code tools

Already listed, not repeated here: dependency-cruiser (JS/TS), import-linter (Python), ArchUnit (Java), ArchUnitNET (.NET), Konsist (Kotlin), go-arch-lint (Go), Mago `guard` (PHP), Packwerk (Ruby).

| Tool | Language | Stars | Last release | Decision |
|---|---|---|---|---|
| [ArchUnitTS](https://github.com/LukasNiessen/ArchUnitTS) | TypeScript | 508 | v2.5.4, 2026-09-13 | Not adopted: overlaps dependency-cruiser. |
| [ts-arch](https://github.com/ts-arch/ts-arch) | TypeScript | 668 | v5.4.1, 2024-12-23 | Not adopted: no release for 22 months. |
| [PyTestArch](https://github.com/zyskarch/pytestarch) | Python | 176 | v5.1.0, 2026-10-24 | Not adopted: overlaps import-linter; small. |
| [PHPat](https://github.com/carlosas/phpat) | PHP | 1.3k | 0.12.5, 2026-09-15 | Not adopted: Mago `guard` covers architecture rules. |

Stars, release dates and licences (all MIT or Apache-2.0) are from the GitHub API on 2026-10-25; the decisions are comparisons by feature set, not runs.

## Structural search alternatives to ast-grep

| Tool | Stars | Last release | Decision |
|---|---|---|---|
| [GritQL](https://github.com/biomejs/gritql) | 4.6k | v0.0.3, 2026-03-30 | Not adopted: pre-1.0, its own query language, mainly a Biome building block. |
| [Comby](https://github.com/comby-tools/comby) | 2.7k | 1.8.1, 2022-06-28 | Not adopted: no release since 2022; text-pattern matching, not tree-sitter. |
| [Opengrep](https://github.com/opengrep/opengrep) | n/a | n/a | Kept for data-flow rules; ast-grep for syntax rules. |

# GitHub Actions: jactionlint, actionlint, zizmor

Reviewed 2026-10-23. Decision: **recommend jactionlint alone by default.** Add zizmor only under the conditions below. Do not recommend actionlint.

## State of the three tools

| | [jactionlint](https://github.com/jdx/jactionlint) | [actionlint](https://github.com/rhysd/actionlint) | [zizmor](https://github.com/zizmorcore/zizmor) |
|---|---|---|---|
| Purpose | Correctness, security and policy | Correctness (syntax, expressions, shellcheck) | Security audits |
| Repository created | 2026-10-05 | n/a (original project) | n/a |
| Last push | 2026-10-21 | 2026-07-16 | 2026-10-23 |
| Latest release | v2.3.0 (2026-10-21), 7 releases | v1.7.12 (2026-03-30) | v1.31.1 (2026-10-15) |
| Stars | 280 | 4.3k | 6.8k |
| Licence | MIT | MIT | MIT |
| Archived or deprecated | No | No | No |

Figures come from the GitHub API on the review date.

## What jactionlint covers

Sources: its [README](https://github.com/jdx/jactionlint#readme), [docs/actionlint.md](https://github.com/jdx/jactionlint/blob/main/docs/actionlint.md) and [docs/zizmor-parity.md](https://github.com/jdx/jactionlint/blob/main/docs/zizmor-parity.md).

- **actionlint:** it is a fork. The `correctness` profile gives the actionlint checks and reads the same config file; it adds rules for more mistakes.
- **zizmor:** it has a rule for each audit of zizmor 1.30.1, with the same ID except `unsound-condition` (reported as `if-always-true`). It also adds its own rules, such as `missing-timeout`, `require-shell`, `mutable-runner-label` and `unused-needs`.
- **Fixes:** `--fix` and `--diff`. With `--online`, `unpinned-uses` is fixed by replacing the tag with its commit SHA and a version comment, so a separate pinning tool is not needed. Image digests need `--fix=unsafe`.
- **Adoption:** profiles (`correctness`, `default`, `pedantic`), a baseline that fails only on new findings, `# zizmor: ignore[...]` comments honoured.
- **Network:** offline unless `--online`.
- **Output:** text, JSON, JSONL, SARIF, GitHub annotations. Exit code 1 on findings of level `error`.

## How good is the parity claim?

The numbers are **published by the jactionlint maintainer**, from [zizmor-measurements.md](https://github.com/jdx/jactionlint/blob/main/docs/zizmor-measurements.md). They are not independent.

- 24-repository run (reproducible): jactionlint also reports 955 of 998 zizmor findings (95.7%).
- 1,109-repository run: 104,421 of 112,559 (92.8%). The corpus and jactionlint commit are **not recorded**, so this cannot be reproduced.
- The maintainer attributes the misses to deliberate differences (for example `excessive-permissions` in reusable-only workflows) or positions that differ by a few lines. We have not checked these claims.

Treat parity as "close and documented", not "identical".

## Known gaps against zizmor

From the parity page, "Known gaps":

- No offline `archived-uses` (jactionlint needs `--online`).
- No pre-commit configuration audit and no language-server mode.
- No per-finding confidence grading.
- `bot-conditions` does not report a negated bot test.
- Some rules report at a different line than zizmor.

## When to add zizmor

Add [zizmor](https://github.com/zizmorcore/zizmor) next to jactionlint if one of these applies:

- you want a second, independent implementation for security-critical repositories;
- you need archived-action detection with no network access;
- you audit `.pre-commit-config.yaml` or want editor integration through its LSP;
- your organization already runs zizmor and relies on its persona and confidence grading.

Running both is a deliberate choice, not the default. Expect overlapping findings.

## Why not actionlint

jactionlint's `correctness` profile covers its checks, and the project is a continuation of it. actionlint's last release was 2026-03-30 and its last push 2026-07-16; it still works, and a repository that only wants syntax checks can keep using it. We do not recommend it for new setups. Packages named `actionlint` (for example in Homebrew core) install the original project, not the fork.

## Why not a separate pinning tool

[pinact](https://github.com/suzuki-shunsuke/pinact) pins actions to SHAs, and jactionlint also does that with `--online --fix`. Use pinact only if you want pinning as a standalone step without adopting the linter.

## Risks of this recommendation

- **Age and bus factor.** The project is weeks old and has one maintainer. Review again on every minor release and if releases stop.
- **Self-reported parity** (see above).
- **Default profile is strict.** It enforces SHA pinning, `permissions:`, timeouts and concurrency. Start with `--baseline-write` on an existing repository.

## What we did not check

We did not run jactionlint and zizmor side by side on a shared corpus, and did not read their rule implementations. The recommendation rests on the maintainer's documentation, repository activity and a test run of jactionlint on this repository's own workflows.

## Re-review triggers

- A release of zizmor or jactionlint that changes rule coverage.
- jactionlint inactivity for 60 days.
- An independent comparison.

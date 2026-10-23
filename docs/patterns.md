# Setup patterns

Tools alone do not enforce anything. These patterns decide when they run. They come from real repositories, for example [sphericon](https://github.com/getsphericon/sphericon), which runs jactionlint, zizmor, gitleaks, typos, knip, ast-grep, commitlint and golangci-lint together. Adapt, do not copy.

## Three tiers

1. **Staged-file hook (fast).** Only checks that run in seconds on changed files: secrets on staged content, linters, formatters, spell check, commit message format.
2. **Pre-push hook (slow).** Whole-project checks: type check, full linter, dependency tidiness.
3. **CI (complete).** Everything, including checks that need the network or a database. CI is the only gate that cannot be skipped.

A hook is a convenience. A check that exists only in a hook is not enforced.

## One toolchain file

Pin the versions of all tools in one file that both developers and CI read, such as a `mise.toml`. CI then runs exactly what the hook ran. Add one aggregate task (`check`) that runs every check, and call that from CI.

## Generated code gate

Regenerate generated files in CI and fail if `git status --porcelain` shows a difference. This catches hand edits and stale output.

## Tests for the rules

Test custom rules. `ast-grep test` runs rule fixtures and snapshots; keep them in the repository next to the rules.

## Custom analyzers

`golangci-lint custom` builds a golangci-lint binary with your own analyzers. Pin its version to the one used by the rest of the toolchain, and check that pin in CI.

## Exceptions

Keep suppressions narrow (path and rule, not a whole directory), and record why. Prefer a baseline over disabling a rule when adopting a check on an old code base.

## Dependabot cooldown

A `cooldown` with `default-days` in `dependabot.yml` delays updates to freshly published versions, which reduces exposure to compromised releases. jactionlint checks this (`dependabot-cooldown`).

## Reporting versus enforcing

Run slow scans that depend on external data (a vulnerability database, for example) on a schedule, not on every pull request. A new advisory can fail a build without any change on your side.

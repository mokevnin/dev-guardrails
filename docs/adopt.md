# Adopt Dev Guardrails in your project

This page is written for a coding agent that was asked to apply Dev Guardrails to a repository. A person can follow it too.

The list is **not a stack to install**. The job is to pick the few entries that fit the project, wire them so that they fail the build, and leave a repository that checks itself.

## Prompt

Give your agent this, from the root of your project:

```text
Apply https://github.com/mokevnin/dev-guardrails to this repository.
Read and follow https://raw.githubusercontent.com/mokevnin/dev-guardrails/main/docs/adopt.md.
Show me the plan before you change anything.
```

## Sources

Read these, in this order:

1. [`README.md`](../README.md): principles and the recommendations by category. It lists what each tool does and where it stops working.
2. [`tools.json`](https://raw.githubusercontent.com/mokevnin/dev-guardrails/main/tools.json): the same entries as data (`category`, `repo`, `rationale`, `limitations`, `last_reviewed`, `details`). Use it to filter by category instead of parsing the README.
3. [`patterns.md`](patterns.md): when the tools run (hooks, CI), and how to handle exceptions and old code.
4. Each chosen entry's `details` file in [`research/`](../research/), if it has one.

Only entries under **Recommendations** are recommendations. **Under review** and [`not-adopted.md`](not-adopted.md) are not; do not install from them. A category with no entry stays empty: say so in your report, do not fill it from memory.

## Steps

### 1. Inspect the project

Record, before choosing anything:

- languages and frameworks (look at manifests and lockfiles, not file extensions alone);
- package managers and how tools are installed today (`mise.toml`, `.tool-versions`, `package.json` scripts, `Makefile`);
- monorepo or single package;
- CI (`.github/workflows`, `.gitlab-ci.yml`) and what it already runs;
- git hooks already in use (husky, lefthook, pre-commit, hk);
- existing linter, formatter and type-checker configuration;
- Dockerfiles, Terraform, Kubernetes manifests, database migrations, an OpenAPI or GraphQL schema;
- existing `AGENTS.md`, `CLAUDE.md` or similar instruction files.

### 2. Choose

Match the findings to README categories. For each category that applies:

- If the project already has a tool that does the same job and runs in CI, **keep it**. Replace it only when the user asked, and say what the replacement fixes.
- Otherwise take the recommended tool. Read its **Limits** and decide whether they apply here (monorepo-only, framework-only, pre-1.0, licence).
- Skip categories that do not apply. A Go-only project gets no Python entries.

Always consider the cross-cutting categories: Secrets, Vulnerabilities, Dependency updates, Config files, Git hooks, Toolchain and, for GitHub Actions or GitLab CI, the CI linter.

Check currency. Each entry has `last_reviewed`; the list is a snapshot. Before pinning, confirm the tool is still maintained and look up its latest release instead of copying a version from this repository.

### 3. Show the plan, then wait

Show the user a short plan and wait for approval:

| Tool | Job | Replaces or adds | Files it will touch | Known limit that matters here |
|---|---|---|---|---|

Also say what you will **not** adopt and why. Ask only when a decision is the user's: replacing a tool they use, adding a paid or copyleft tool, or a check that will fail on existing code and needs a baseline.

### 4. Wire it so it enforces

Follow [`patterns.md`](patterns.md):

- **One toolchain file** that developers and CI both read. Pin tool versions in it. `mise.toml` is the pattern used in this repository; keep the project's own if it already has one.
- **One aggregate command** (`check`) that runs every check, and an optional `fix` for the safe autofixes. CI calls the same command, so a hook and CI cannot drift apart.
- **Three tiers.** Fast checks on staged files in the commit hook, whole-project checks on push, everything in CI. A check that exists only in a hook is not enforced.
- **CI is the gate.** Add or extend a workflow that runs the aggregate command. Pin actions to a full commit SHA.
- Slow scans that depend on external data (vulnerability databases) run on a schedule as well, not only on pull requests.

Every check must exit non-zero on a violation. Some tools do not by default (a linter that exits 0 on warnings, a scanner that exits 0 with JSON output). The tool's **Limits** say so; configure it or gate on the output that does fail.

### 5. Adopt on existing code

A new check on an old code base will fail. Do not hide that.

1. Run each tool across the whole project and count the findings per rule.
2. Fix mechanical findings with the tool's safe autofix, one tool per commit, and read the diff. Never run an autofix that deletes code (for example Knip's `--fix`) unattended.
3. For the rest, use the tool's **baseline** (for example `--ignore-known` in dependency-cruiser) so that new violations fail while old ones are listed.
4. Where a rule cannot be satisfied, add a narrow exception: one path and one rule, with a reason. Do not turn the rule off. Give suppressions that hide a security or risk finding a review date, as in [Review dates on exceptions](patterns.md#review-dates-on-exceptions).

### 6. Prove it works

For every tool you added, show that it can fail:

- run the aggregate command on the clean tree and report the result;
- introduce one real violation on a scratch branch (a stale import, a fake secret, a badly formatted file), confirm the command exits non-zero, and revert it;
- open the pull request and confirm the CI job runs the same command and its result is visible.

A check that was never seen failing is not known to work. If you could not run something (it needs a network, a database or a token), say so.

### 7. Write the rules for agents

Add to the project's `AGENTS.md` (or the file its agents already read), following [Rules for AI agents](patterns.md#rules-for-ai-agents):

- the command that runs every check, and that it must pass before a change is done;
- generated files, which are never edited by hand;
- lint rules are never disabled to get a change through: exceptions are narrow, carry a reason and need a human decision.

Keep it short, and keep only rules that a check backs. If agnix is adopted, it lints these files too.

### 8. Report

Finish with a short report, not a log:

- what was added, with the file list;
- what was kept as it was, and what was skipped, each with the reason;
- the baseline and exceptions you created, and how many findings they hold;
- categories where the list has no recommendation;
- checks you could not run.

Land the work as small commits or pull requests, one tool or one concern at a time, so each can be reviewed and reverted alone.

## Do not

- Install every entry, or add a tool for a category the project does not have.
- Pick a tool from **Under review** or `not-adopted.md`.
- Change the project's existing standards in the same change that adds a check.
- Turn a check into a warning to make it pass.
- Copy tool versions, hook layouts or config from this repository without checking them against the project: they fit its stack, not yours.

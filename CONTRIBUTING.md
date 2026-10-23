# Contributing

Thank you for helping. Please read this before opening a pull request.

**A new tool is not accepted because it is good. It must fill a gap, or show a compelling advantage over the current recommendation.** Most good tools will not be added, and that is the point of the list.

## What we accept

- A tool for a **missing category** (see [Under review](README.md#under-review)).
- A **replacement** for a current recommendation, with a written comparison.
- A fix for **outdated information**: a deprecated tool, a moved repository, a changed licence.
- **Removal** of an unmaintained tool.
- Better [selection criteria](#selection-criteria) or docs.
- A clarification of an existing entry: limits, conditions, overlap.

## What we reject

- Another alternative for a job that already has a recommendation, without a comparison.
- Tools that only advise and cannot fail a build.
- Tools with no public repository or documentation.
- Promotion of your own tool without the same evidence we would ask of anyone else.
- Bulk additions. One tool or one change per pull request.

## Requirements for a pull request

The [pull request template](.github/PULL_REQUEST_TEMPLATE.md) mirrors this list. Every point needs an answer in the description.

1. **Enforcement.** The tool automatically checks a development standard. Say which one.
2. **Public source.** There is an official public repository and documentation.
3. **Currency check.** Record the last release, recent meaningful commits, maintainer activity, archived or deprecated status, known successors or forks, and open critical issues. Activity older than 30 days is a reason to look closer, not an automatic rejection; stable tools can be exceptions if you say why. There is no minimum project age: a new tool or fork can beat an old one.
4. **Alternatives.** Name the main current alternatives and compare features, rule coverage, speed, integration and configuration.
5. **Overlap.** Say what it overlaps with among already recommended tools. If it replaces several checks, say which ones. Do not recommend two tools that mostly do the same thing.
6. **Why this one.** Explain why it should be added or should replace the current recommendation.
7. **Limits.** State the significant limitations and conditions of use.
8. **Style.** Follow the README format below and update `tools.json`.

## Selection criteria

A tool is better when it:

- runs from the CLI, non-interactively, and exits non-zero on violations;
- works in CI and gives clear diagnostics;
- has machine-readable output (JSON, SARIF);
- can fix problems automatically where that is safe;
- allows custom rules;
- is fast and cheap to run;
- covers more checks than the tool it competes with.

Not every point is required, but they decide close calls. Automated signals (a new release, no recent commits) are inputs, not verdicts. They do not replace a comparison.

## Entry format

Add an entry to the right category in `README.md`:

```markdown
- **[Name](https://github.com/owner/repo)**: what it enforces, and why it was chosen. *Limits:* the important constraints.
```

Keep it to a few sentences. Longer comparisons go in `research/<topic>.md` and are linked from the entry.

Then add a record to `tools.json`:

| Field | Meaning |
|---|---|
| `id`, `repo`, `category` | Name, `owner/repo` on GitHub, category as in the README. |
| `last_reviewed` | Date (`YYYY-MM-DD`) you did the currency check. |
| `sources` | URLs or repository paths used for the decision. |
| `rationale` | Why it was chosen. |
| `stable_exception` | Optional `true` for a finished tool with old releases; mute the push-age and release-age flags. Explain it in `limitations`. |
| `limitations` | What it does not do. |

Run `npm ci && npm run check:registry` to validate the file. Scripts in this repository are written in TypeScript (`scripts/`, run directly by Node 24 and checked with `npm run typecheck`).

## Checks

The `Lint` workflow runs markdownlint-cli2, lychee, jactionlint on this repository's own workflows, and the registry check. Run them locally before you push. Pin every action in this repository to a full commit SHA with a version comment.

## Removing or replacing a tool

Open a pull request that edits the entry and `tools.json`. For a removal, link the evidence (archived repository, announced end of life, unfixed critical issue). For a replacement, include the comparison required above, and say what a user of the old tool has to change. Add a row to [docs/not-adopted.md](docs/not-adopted.md) for the tool that was rejected or replaced.

## Conduct

Be kind and be specific. Disagree with the evidence, not the person.

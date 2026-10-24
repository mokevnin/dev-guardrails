# Not adopted, and why

Tools we looked at and did **not** recommend, as of 2026-10-23. This keeps the same question from being asked again, and shows what would change the answer. It is a record of decisions, not a list of bad tools.

Reasons used below:

- **Superseded:** a newer tool covers it.
- **Overlap:** another recommendation already does the job.
- **Unverified:** not compared yet; sits in [Under review](../README.md#under-review).
- **Not enforcement:** it reports or advises, it does not fail a build.
- **Stale or risky:** maintenance or supply-chain signals.

## Rejected for now

| Tool | Reason | What would change the answer |
|---|---|---|
| [actionlint](https://github.com/rhysd/actionlint) | Superseded by jactionlint, whose `correctness` profile covers it. Last release 2026-03-30. | jactionlint becomes unmaintained. |
| [zizmor](https://github.com/zizmorcore/zizmor) (by default) | Overlap: jactionlint has a rule for each zizmor audit. Allowed as an addition in the cases listed in [research/github-actions.md](../research/github-actions.md). | An independent comparison finding real gaps in jactionlint. |
| [pinact](https://github.com/suzuki-shunsuke/pinact) | Overlap: `jactionlint --online --fix` pins tags to commit SHAs. | You want pinning without adopting a linter. |
| [cspell](https://github.com/streetsidesoftware/cspell) | Overlap with typos, which has fewer false positives and needs little setup. | You need project dictionaries or many natural languages. |
| [detect-secrets](https://github.com/Yelp/detect-secrets) | Stale: last release v1.5.0 on 2024-05-06. | A new release and a comparison with the other secret scanners. |
| [rumdl](https://github.com/rvben/rumdl) | Candidate to re-review: pre-1.0 (v0.3.0), licence not detected. | A 1.0 release with rule parity against markdownlint. |
| [cocogitto](https://github.com/cocogitto/cocogitto), [committed](https://github.com/crate-ci/committed) | Not clearly better than commitlint. Last release 2026-03-04 and 2026-02-25. | Active development and a single-binary advantage that matters to you. |
| [Bandit](https://github.com/PyCQA/bandit) | Overlap with the Ruff `S` rules. | You need custom Bandit plugins. |
| [pydocstyle](https://github.com/PyCQA/pydocstyle) | Archived 2023-11-03; Ruff `D` rules replace it. | None. |
| [Psalm](https://github.com/vimeo/psalm) | PHPStan has the wider extension set; Psalm 7.0 was still a release candidate when reviewed. | A stable 7.0 and a comparison on your codebase. |
| qossmic/deptrac | Archived and moved; use [deptrac/deptrac](https://github.com/deptrac/deptrac). | None. |
| [phpcpd](https://github.com/sebastianbergmann/phpcpd) | Archived 2023-01-10. | None. |
| [Brakeman](https://github.com/presidentbeef/brakeman) | Licence is non-commercial only (Brakeman Public Use License); commercial use needs a paid licence. Kept in [Under review](../README.md#under-review). | A licence change, or your use being non-commercial. |
| [Atlas](https://github.com/ariga/atlas) migration lint | Checks that matter for locks and downtime (`PG1xx`, `PG3xx`) are labelled Atlas Pro; extra checks need `atlas login` ([analyzers](https://atlasgo.io/lint/analyzers)). squawk covers PostgreSQL lock safety without that. | The checks you need move to the free edition. |
| [Gitleaks](https://github.com/gitleaks/gitleaks) | Latest release v8.30.1 (2026-03-21); Betterleaks is recommended instead and reads the same kind of config. | A new Gitleaks release line and a comparison. |
| [cargo-audit](https://github.com/rustsec/rustsec) | cargo-deny covers the RustSec advisory check and more. | You only want advisories and no policy file. |

## Held back (Unverified)

Not rejected: these are in [Under review](../README.md#under-review) because we have not compared the candidates properly.

- **Trivy.** In March 2026 trivy-action tags and a release were compromised ([advisory](https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23)). OSV-Scanner is recommended for lockfile vulnerabilities; for container images and IaC security Trivy, Grype and Checkov are still compared.
- **TruffleHog and Kingfisher.** Alternatives to Betterleaks; TruffleHog is AGPL-3.0.
- **Biome and Oxlint.** ESLint with Prettier is recommended; Oxlint is the fast alternative but exits 0 on warnings by default, and oxfmt is pre-1.0.
- **Semgrep and Opengrep.** Needed only for data-flow rules; ast-grep covers syntax rules.
- **Hook runners** (hk, prek, pre-commit, Lefthook), **Docker, Terraform, Kubernetes, API contracts, SQL, architecture, YAML, supply chain.** See the table in the README.

## Seen in sphericon, not taken

[sphericon](https://github.com/getsphericon/sphericon) is a source of candidates, not a list to copy.

| Item | Reason |
|---|---|
| hk, vacuum, squawk, oxfmt, govulncheck, OpenSSF Scorecard, go-test-coverage | Not compared with alternatives yet, so not recommended. |
| mise, release-please | Toolchain and release automation, not enforcement. |
| CodeQL | Not checked against the other security scanners. |
| pinact, zizmor next to jactionlint | Overlap, see above. |

schemalens was adopted after the same review with its conflict of interest stated in the entry. What we did take: typos, ast-grep rules with tests, Dependabot `cooldown`, and the patterns in [patterns.md](patterns.md).

## Adding to this file

When a pull request rejects or replaces a tool, add a row with the reason and what would change the answer.

# KICS: IaC and Docker Compose security

Reviewed 2026-10-24. **Keep the general IaC category under review; add KICS as a research lead.** The strongest reason to evaluate it is Docker Compose security, rather than another Dockerfile checker. This comparison executes three scanners on six small files; it does not establish comparative detection quality on real projects.

## Currency and provenance

- [KICS v2.2.0](https://github.com/Checkmarx/kics/releases/tag/v2.2.0) was published 2026-09-17. [The repository](https://github.com/Checkmarx/kics) is not archived or marked deprecated; its licence is Apache-2.0.
- Maintenance is substantive: [2026-10-15 query-ID fix](https://github.com/Checkmarx/kics/commit/d06cb64730486599bcb34dea013372cebb7cae5a); [2026-10-20 release build fix](https://github.com/Checkmarx/kics/commit/1f05308bc1f1). Recent release work involves Checkmarx accounts including `cx-artur-ribeiro`, `cx-andre-pereira` and `cx-ricardo-jesus`. Release notes include Dockerfile parsing and query fixes.
- No announced replacement or successor was found in the official repository/release documentation. The most-starred forks inspected did not advertise a successor. This is a bounded check, not proof none exists.
- The public repository security-advisory API returned zero entries; an open-issue search for the `critical` label returned zero. Neither proves absence of vulnerabilities. Relevant open reports include [Dockerfile false negative #8152](https://github.com/Checkmarx/kics/issues/8152), [Terraform locals resolution #8144](https://github.com/Checkmarx/kics/issues/8144), [Compose anonymous-volume false positive #8047](https://github.com/Checkmarx/kics/issues/8047), and [SARIF duplicate taxa #7588](https://github.com/Checkmarx/kics/issues/7588).
- This release has no downloadable binary assets. Use the image or build from source; [prebuilt binary request #7833](https://github.com/Checkmarx/kics/issues/7833) remains open. Pin images by digest, not `latest`.

## Scope and alternatives

| Tool | Dockerfile | Docker Compose | Terraform | Custom policies / integration |
|---|---|---|---|---|
| [KICS](https://docs.kics.io/latest/platforms/) | Security and best practices | Dedicated platform and built-in rules | Source and plan support | Rego queries; severity and query/result exclusions; JSON/SARIF; some query-specific remediation |
| [Trivy config](https://trivy.dev/docs/latest/scanner/misconfiguration/) | Misconfigurations | Not listed as a supported IaC type; no Compose findings in this test | Source and plan support | Rego; severity filtering and ignore controls; JSON/SARIF; same binary as image scanner |
| [Checkov](https://www.checkov.io/2.Basics/CLI%20Command%20Reference.html) | Security and best practices | No Compose framework in tested CLI; no built-in Compose coverage demonstrated | Source/plan plus graph checks | Python/YAML custom policies; skip/check controls; JSON/SARIF; Python runtime or container |
| [Hadolint](https://github.com/hadolint/hadolint) | Dockerfile practices and embedded ShellCheck | No | No | Focused Dockerfile linter, already recommended |

These scope statements follow the official supported-platform lists and tested CLI, not raw rule-count comparisons. Generic YAML parsing or custom checks are not the same as built-in Compose security policies. Hadolint does not inspect runtime Compose privileges. KICS is not a replacement for image package CVE scanning by Trivy, Grype or Docker Scout; parsing a Dockerfile does not inspect installed packages. [kube-linter](https://github.com/stackrox/kube-linter) remains a narrower manifests/Helm alternative, not a Compose or Terraform scanner.

KICS overlaps heavily with Trivy/Checkov for Terraform and Dockerfile. The case for an additional tool is therefore conditional: repositories with important Compose runtime configuration can evaluate KICS against that gap. Repositories already using Trivy without Compose may gain little from another general scanner. No evidence here justifies replacing Hadolint, TFLint, Trivy or Checkov globally.

## Executed experiment

Inputs are in [fixtures/kics](fixtures/kics/). They contain no credentials or download commands and were not deployed. **Only scan the text; never build or start these deliberately insecure examples.** The `hardened` files are narrow controls for the selected hazards, not universally compliant infrastructure.

Pinned scanner/policy provenance:

| Component | Tested version / policy source |
|---|---|
| KICS | 2.2.0, image `checkmarx/kics@sha256:ef29dbac14b046b1ef65f3280646112e927a61781c5f01bca1aeb723e0b96003`; queries and libraries bundled in that image; network disabled |
| Trivy | 0.76.1, official macOS ARM64 archive SHA-256 `11a9b6cd2752011b54f01ea4bd0dbfa9f0c41dc6538d5a3f9d23955f471bf4e5`; fresh isolated cache and `--skip-check-update` force embedded checks from that release, not a moving downloaded policy bundle |
| Checkov | 3.3.30, Python 3.12 isolated environment; bundled checks, `--skip-download`, no API key or external policies |

[Trivy release/checksums](https://github.com/aquasecurity/trivy/releases/tag/v0.76.1), [Checkov release](https://github.com/bridgecrewio/checkov/releases/tag/3.3.30). The Trivy archive checksum matched the official checksum file. These pins fix scanner/policy versions, not perpetual currency; refresh versions and reassess before adopting. Checkov's transitive Python dependencies were resolved during installation, so preserve an environment lock when comparing hosts. The existing [Trivy supply-chain discussion](cross-cutting.md#2-vulnerabilities-and-sca) still applies.

With all built-in rules enabled for Dockerfile/Terraform and KICS Compose:

| Scanner | Narrow-control findings / exit | Misconfigured findings / exit |
|---|---|---|
| KICS | 4 / 30 | 18 / 50 |
| Trivy (`--exit-code 1`) | 0 / 0 | 6 / 1 |
| Checkov | 1 / 1 | 6 / 1 |

Finding totals are not a score: severity, aggregation and policy intent differ. KICS's four remaining controls findings concern an absent IAM Access Analyzer, private-network scope, missing tags and unattached security group; Checkov flags the unattached group. These examples intentionally omit a complete AWS deployment.

All three detected explicit root in the Dockerfile and public SSH ingress in Terraform. KICS additionally reported Compose privileged mode, sensitive host mount, shared PID/network namespaces, missing capability restrictions, missing security options and healthcheck. Trivy and Checkov emitted no Compose security results. Narrow controls pass only when selecting KICS's three matching rules (root, privileged Compose, public SSH), or Checkov's root/public-SSH checks. This verifies specific transitions, not blanket security.

The full-corpus single runs took approximately 11 seconds per KICS container, 0.5–0.8 seconds for Trivy and 1.3–1.5 seconds for Checkov on an Apple Silicon Mac. Startup, Docker overhead and unequal coverage dominate; no repetitions or controlled performance benchmark were performed.

## Enforcement and reproduction

[The runner](fixtures/kics/run.py) records commands, outputs, exit codes and wall times in a caller-selected empty directory. It never starts fixture services. Install the pinned releases above in an isolated environment, put their executables on `PATH`, then run:

```sh
python3 research/fixtures/kics/run.py /tmp/kics-comparison
```

The runner executes all-rule and selected-rule controls and tests Trivy's default exit behavior. Review the generated JSON reports as well as exit codes: unsupported files can produce no findings without an error. Reproduction requires Docker and downloading the pinned KICS image in advance if the daemon cannot pull it. Do not include generated reports or scanner caches in the PR.

[Documented KICS flags](https://github.com/Checkmarx/kics/blob/v2.2.0/docs/commands.md) matter: `--ci` changes presentation, not enforcement; `--fail-on` defaults to all finding severities, and `--ignore-on-exit` defaults to `none`. The experiment verifies default nonzero finding exits. Explicit `--fail-on high,critical` is clearer than assuming only severe findings fail. Do not use `--ignore-on-exit results` or `all` for a blocking gate.

Trivy defaults to exit 0 even with findings; the experiment also runs without `--exit-code 1` to demonstrate this. Checkov fails on failed checks unless `--soft-fail` or related overrides are configured; [hard/soft-fail documentation](https://www.checkov.io/2.Basics/Hard%20and%20soft%20fail.html). Match severities/check intent before comparing CI behavior.

## Decision and remaining work

Add KICS to the existing under-review row with this evidence, without an adopted `tools.json` entry. Dedicated Compose rules are a meaningful gap worth further evaluation, but six files do not settle the general IaC choice. Before recommending KICS, test real multi-file Compose overrides/interpolation, Terraform modules/locals, parser failures, suppressions and SARIF ingestion; measure false positives and missed hazards on a larger independently designed corpus. The open issue reports above are reasons to test these paths, not assertions reproduced by this experiment.

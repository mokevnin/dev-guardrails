# PHPMD versus Mago: additional metric budgets

Reviewed **2026-10-24**. PHPMD can be a narrow companion for teams that explicitly need NPath, LOC, numeric coupling or public-surface budgets. It is not a replacement for the recommended Mago toolchain, and most ordinary lint checks are not a reason to run both. This change records an evidence-backed candidate under review, without adding another general PHP linter to the registry.

## Currency

| Tool | Tested stable release | Maintenance and licence |
|---|---|---|
| [PHPMD](https://github.com/phpmd/phpmd) | [3.0.0, 2026-10-04](https://github.com/phpmd/phpmd/releases/tag/3.0.0) | BSD-3-Clause, PHP 8.1 or later, not archived. Recent substantive work includes [XML ruleset loading](https://github.com/phpmd/phpmd/commit/bc69f061235285e5112f644d8e709b0f5cba5dcc) and [interpolated-field handling](https://github.com/phpmd/phpmd/commit/e1c35e388283a8baa80489c1478a5508649db7a2), both after the tested release. |
| [Mago](https://github.com/carthage-software/mago) | [1.58.2, 2026-10-19](https://github.com/carthage-software/mago/releases/tag/1.58.2) | MIT OR Apache-2.0, not archived. The release fixes parser recovery for unfinished static accesses; subsequent [union-narrowing work](https://github.com/carthage-software/mago/commit/923c061bad21b90a785a4512885dfa37f5c44416) is outside this release test. |

PHPMD's [Composer metadata](https://github.com/phpmd/phpmd/blob/3.0.0/composer.json) lists Manuel Pichler as founder and Marc Würth as maintainer; AJenbo published 3.0.0 and contributes current fixes. Mago's release and fixes are led by azjezz / Seifeddine Gmati. These are observed maintainer signals, not a bus-factor measurement. Neither official repository/release history announced deprecation or a designated successor; the check does not rule out every fork. No unreleased fix was substituted for a stable tool in this experiment.

Relevant public reports include PHPMD [XML configuration on PHP 8.3 #1364](https://github.com/phpmd/phpmd/issues/1364), [void/static parsing #1363](https://github.com/phpmd/phpmd/issues/1363), [arrow-function unused-variable findings #1306](https://github.com/phpmd/phpmd/issues/1306) and [private fields with traits #602](https://github.com/phpmd/phpmd/issues/602), plus Mago [name validation #2556](https://github.com/carthage-software/mago/issues/2556). These reports were reviewed, not independently reproduced here. The XML fix is newer than PHPMD 3.0.0; the runner uses YAML. Mago's [2.0 planning #1931](https://github.com/carthage-software/mago/issues/1931) is not a released replacement for 1.58.2.

## Comparison method

The [runner](fixtures/phpmd-mago/run.py) generates PHP examples and configurations in an empty output directory, then saves every command, JSON report and stderr stream. It never executes the generated PHP. Environment: macOS arm64, PHP 8.5.9; Mago parses the fixtures as PHP 8.2. No framework, vendor code, custom extension, baseline or automatic fix is involved.

There are **20 threshold cases** (a control and an over-budget case for ten policies), a separate Halstead-overlap case, and one malformed-input case: **65 scanner invocations**. Assertions check exit codes and diagnostic identities, not merely whether a tool printed something.

Each threshold case runs:

1. PHPMD with only the named rule and an explicit maximum.
2. Mago with its four related metric rules and matched thresholds where applicable: `cyclomatic-complexity`, `too-many-methods`, `too-many-properties`, `excessive-parameter-list`.
3. A second Mago pass with all **191 built-in rules** from the release catalog explicitly enabled at error severity, retaining the same metric options. Framework integrations remain unconfigured; arbitrary external extensions are not compared.

**Do not use `--pedantic` to preserve project thresholds.** In 1.58.2 it [replaces configured rule settings with defaults and enables all integrations](https://github.com/carthage-software/mago/blob/1.58.2/src/utils/mod.rs#L82-L94). The runner uses it only to enumerate the catalog, then writes a full explicit configuration. A preliminary experiment confirmed that a configured method threshold of 3 was enforced with `--only` but reset by `--pedantic`. Positive overlap controls below verify that the final full-rule pass actually retains the configured thresholds.

## Executed results

Every threshold control passed both tools, including the full Mago pass. This table describes the over-budget counterpart. `2` is a PHPMD violation exit, `1` a Mago failure, and `0` success.

| Policy / input | PHPMD result | Mago metric pass / full-rule pass | Interpretation |
|---|---|---|---|
| Method cyclomatic complexity 4, maximum 3 | 2: `CyclomaticComplexity` | 1 / 1: `cyclomatic-complexity` | Existing overlap. Mago's `method-threshold` was explicitly set. |
| Six parameters, maximum 5 | 2: `ExcessiveParameterList` | 1 / 1: `excessive-parameter-list` | Existing overlap. |
| Six ordinary methods, maximum 5 | 2: `TooManyMethods` | 1 / 1: `too-many-methods` | Existing overlap; getter/setter counting was enabled explicitly. |
| Six declared properties, maximum 5 | 2: `TooManyFields` | 1 / 1: `too-many-properties` | Existing overlap; promoted/hooked properties were not tested. |
| Eight independent `if` statements: NPath 256, maximum 200; method CC 9 | 2: `NPathComplexity` | 0 / 0 | Added acyclic-path budget. Method CC remains below the configured Mago maximum 10. |
| Straight-line field mapping: method LOC 25, maximum 15 | 2: `ExcessiveMethodLength` | 0 / 0 | Added direct method-size budget on this fixture. |
| Same mapping: class LOC 29, maximum 25 | 2: `ExcessiveClassLength` | 0 / 0 | Added direct class-size budget on this fixture. |
| References to six declared collaborator classes, CBO maximum 5 | 2: `CouplingBetweenObjects` | 0 / 0 | Added numeric dependency-count budget. |
| Three public methods plus three public fields, combined maximum 5 | 2: `ExcessivePublicCount` | 0 / 0 | Added combined public-surface budget; each separate Mago member count stays below 5. |
| Six branch-free methods, WMC maximum 5 | 2: `ExcessiveClassComplexity` | 0 / 0 | Different aggregation, not absence of class complexity in Mago. PHPMD WMC is 6; Mago's branch contribution is 0. |

These deliberately small maxima keep the generated examples reviewable. They are not suggested production settings or a comparison of shipped defaults. The NPath case does use PHPMD's default maximum 200; seven independent `if` statements form its passing NPath 128 control.

For example, the NPath-over case contains this method:

```php
public function evaluate(array $flags): int
{
    $result = 0;
    if ($flags[0]) { $result += 1; }
    if ($flags[1]) { $result += 1; }
    if ($flags[2]) { $result += 1; }
    if ($flags[3]) { $result += 1; }
    if ($flags[4]) { $result += 1; }
    if ($flags[5]) { $result += 1; }
    if ($flags[6]) { $result += 1; }
    if ($flags[7]) { $result += 1; }
    return $result;
}
```

The **additional Halstead case** prevents overinterpreting the LOC rows: twenty repetitions of `$result += 1` also exceed the method LOC budget, but full-rule Mago reports `halstead` and exits 1. Thus PHPMD does not uniquely reject every long method. The field-mapping examples isolate direct LOC limits from the default Halstead volume/difficulty/effort thresholds. Both findings and both limits belong in the comparison.

Malformed PHP exits **3** with PHPMD processing errors and **1** with Mago `parse` diagnostics. The runner asserts both; neither failure is counted as a successful policy check.

## Why the metrics differ

The versioned [PHPMD code-size rules](https://github.com/phpmd/phpmd/blob/3.0.0/rulesets/codesize.xml) and [design rules](https://github.com/phpmd/phpmd/blob/3.0.0/rulesets/design.xml) define NPath, LOC, WMC, CBO and public-surface policies. Mago's [built-in rule tree](https://github.com/carthage-software/mago/tree/1.58.2/crates/linter/src/rule) contains no direct NPath, method/class LOC, CBO or combined-public-count rule found in this review. The full-rule experiment is supporting evidence on these inputs, not a proof about every PHP program.

- [Mago cyclomatic complexity](https://github.com/carthage-software/mago/blob/1.58.2/crates/linter/src/rule/maintainability/cyclomatic_complexity.rs) already covers methods when `method-threshold` is set. Its class aggregation subtracts the entry contribution and skips accessors; PHPMD WMC sums method complexities. Identical numbers do not imply identical budgets. Mago also has method-count controls that can catch a many-methods class under a different policy.
- [Method count](https://github.com/carthage-software/mago/blob/1.58.2/crates/linter/src/rule/maintainability/too_many_methods.rs), [property count](https://github.com/carthage-software/mago/blob/1.58.2/crates/linter/src/rule/maintainability/too_many_properties.rs) and [parameter count](https://github.com/carthage-software/mago/blob/1.58.2/crates/linter/src/rule/maintainability/excessive_parameter_list.rs) overlap PHPMD, but defaults and exclusions differ. The runner does not infer parity for constructors, accessors or property hooks from ordinary-member examples.
- [Halstead](https://github.com/carthage-software/mago/blob/1.58.2/crates/linter/src/rule/maintainability/halstead.rs) estimates volume, difficulty and effort; it is not an equivalent LOC or NPath policy. It can still reject the same input, as the contrast case demonstrates.
- [Mago guard](https://github.com/carthage-software/mago/blob/1.58.2/docs/content/en/tools/guard/configuration-reference.md) controls dependency edges and structural conventions. An allowed/forbidden edge policy differs from a numeric coupling budget. [Analyzer settings](https://github.com/carthage-software/mago/blob/1.58.2/docs/content/en/tools/analyzer/configuration-reference.md) include internal complexity limits for inference performance, not these source-quality budgets. `analyze` and `guard` were reviewed by documentation, not executed here; no claim about type-analysis parity is made.

Do not label cyclomatic complexity or NPath as cognitive complexity. Neither this experiment nor the source review establishes a cognitive-complexity implementation; PHPMD tracks that separately in [#594](https://github.com/phpmd/phpmd/issues/594).

## Reproduction and integration

Download the exact release artifacts above, extract the appropriate Mago binary for the host, then run:

```sh
python3 research/fixtures/phpmd-mago/run.py \
  --phpmd /path/to/phpmd.phar \
  --mago /path/to/mago \
  --output /tmp/phpmd-mago-comparison
```

Use an empty output directory. The runner verifies tool versions, generates inputs/configurations, records the rule catalog, and retains raw diagnostics. The tested artifacts matched their SHA-256 values in GitHub release metadata:

| Artifact | SHA-256 |
|---|---|
| `phpmd.phar` from 3.0.0 | `0d6ba223b7bf41119e02e1ef23faac3cb93e5f0fc6d06ea42211873edf6a8236` |
| `mago-1.58.2-aarch64-apple-darwin.tar.gz` | `e1559205eb1886ca1a55dc0bb96b4f6614713f274920126e3a5bd309c348b987` |

A narrow PHPMD companion policy can enable just the required budgets, for example:

```yaml
rules:
  - ref: rulesets/codesize.xml/NPathComplexity
    properties:
      maximum: 200
  - ref: rulesets/design.xml/CouplingBetweenObjects
    properties:
      maximum: 13
  - ref: rulesets/codesize.xml/ExcessivePublicCount
    properties:
      maximum: 45
```

Run `php phpmd.phar analyze --ruleset phpmd.yml --format json src/` and propagate nonzero exits. These example maxima follow shipped defaults, not a universal quality standard. Avoid duplicating entire clean-code, naming and unused-code rulesets beside Mago without a separate rule-level justification. Unused-symbol checks would require comparing Mago's analyzer as well; they were not evaluated here.

**PHPMD 2 users need a migration review.** The [3.0 upgrade guide](https://github.com/phpmd/phpmd/blob/3.0.0/UPGRADING.md) changes the positional CLI, configuration conventions and upper-bound semantics from `>=` to `>` for several rules. `phpmd migrate --preserve-behavior` adjusts configured values, but defaults not explicitly configured still use the new boundaries. Do not reuse old thresholds and claim equivalent enforcement without checking them. JSON, SARIF, baseline and parallel-processing support are available, but only JSON and single-threaded analysis were exercised here.

## Decision

Keep Mago as the default PHP toolchain. PHPMD adds a defensible, conditional option for **explicit metric budgets** demonstrated above; WMC needs special care because it partially overlaps an existing aggregate metric. Record this distinction under review rather than recommend two broad overlapping lint stacks. A registry recommendation would need agreement on the distinct job and a trial against a real codebase to calibrate thresholds, exceptions, parser coverage and false positives. Additional PHPMD rules such as numeric inheritance depth and public-only method counts remain outside this executed corpus.

No performance benchmark was performed. This experiment measures diagnostic coverage and blocking behavior on deliberately small synthetic inputs, not developer productivity or overall code quality.

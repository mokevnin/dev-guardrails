# Composer dependency hygiene

Reviewed 2026-10-24. This is evidence for the PHP dependencies category, not a
registry addition. Keep it under review until the maintainer accepts the
installation and framework-configuration trade-offs below.

## Finding

**composer-dependency-analyser is the strongest of the three tested candidates
for a single dependency-hygiene gate.** Its released version identified unused,
transitive-only and incorrectly classified dependencies in the same run. Neither
alternative covered all three jobs. A small synthetic comparison establishes
coverage and exit behaviour, not performance or framework compatibility.

The dependency-hygiene question is separate from the existing reference to
`composer audit` in the open category. [Composer validate](https://getcomposer.org/doc/03-cli.md#validate) checks
manifest validity and lock consistency; [audit](https://getcomposer.org/doc/03-cli.md#audit)
checks package advisories and abandonment. Neither infers whether application
symbols justify `require` or `require-dev` declarations. Keep the existing
vulnerability scanner; this proposal does not replace it.

## Currency and maintenance

Sources below were checked against GitHub releases, commits, repository metadata,
contributors and open issues on the review date. All three repositories are
unarchived, MIT licensed and have no deprecation notice in their READMEs.

| Candidate | Latest release | Meaningful maintenance evidence |
|---|---|---|
| [composer-dependency-analyser](https://github.com/shipmonk-rnd/composer-dependency-analyser) | [1.8.4, 2025-11-25](https://github.com/shipmonk-rnd/composer-dependency-analyser/releases/tag/1.8.4) | [2026-08-11: avoid reporting virtual packages and metapackages](https://github.com/shipmonk-rnd/composer-dependency-analyser/commit/93876a3adeb5b040ef28a6f79a1e07309b9ec21c); [2026-06-29: reflection crash fix](https://github.com/shipmonk-rnd/composer-dependency-analyser/commit/2e5db2b98da7151edd6d0e489abb322d5ae7dca6). Both postdate the tested release. |
| [composer-unused](https://github.com/composer-unused/composer-unused) | [0.9.7, 2026-10-23](https://github.com/composer-unused/composer-unused/releases/tag/0.9.7) | [2026-10-23: handle packages without source/dist URLs](https://github.com/composer-unused/composer-unused/commit/e1b1f4b4130b65c5bf036dbf435c0b9fe3f8c020). |
| [ComposerRequireChecker](https://github.com/maglnet/ComposerRequireChecker) | [4.24.0, 2026-03-20](https://github.com/maglnet/ComposerRequireChecker/releases/tag/4.24.0) | [2025-12-29: simplify symbol collection](https://github.com/maglnet/ComposerRequireChecker/commit/95937f5bab7e4988ae228087d85d283a472d6c8e); dependency/workflow maintenance continues in [2026 commit history](https://github.com/maglnet/ComposerRequireChecker/commits/). |

The analyser's old release deserves scrutiny, but meaningful fixes in 2026 rule
out equating release age with abandonment. Its [contributor history](https://github.com/shipmonk-rnd/composer-dependency-analyser/graphs/contributors)
is concentrated around janedbal, with contributions from JanTvrdik and others.
The [fork list](https://github.com/shipmonk-rnd/composer-dependency-analyser/forks)
and project README did not identify a maintained successor; this is a discovery
result, not a guarantee that none exists.

No issue labelled critical was identified in the public open-issue review; that
does not establish absence of vulnerabilities. Relevant unresolved reports:

- Analyser: [global-class false unused](https://github.com/shipmonk-rnd/composer-dependency-analyser/issues/278),
  [Composer replace constraints](https://github.com/shipmonk-rnd/composer-dependency-analyser/issues/230),
  [plugins](https://github.com/shipmonk-rnd/composer-dependency-analyser/issues/226),
  [installers](https://github.com/shipmonk-rnd/composer-dependency-analyser/issues/227)
  and [extension false positives](https://github.com/shipmonk-rnd/composer-dependency-analyser/issues/254).
- composer-unused: [Windows framework configuration](https://github.com/composer-unused/composer-unused/issues/741),
  [PHP 8.5 ext-uri false unused](https://github.com/composer-unused/composer-unused/issues/740)
  and [custom vendor locations](https://github.com/composer-unused/composer-unused/issues/734).
- RequireChecker: [Symfony 8 support](https://github.com/maglnet/ComposerRequireChecker/issues/590)
  and [unknown mb_trim](https://github.com/maglnet/ComposerRequireChecker/issues/578).

## Executed comparison

Environment: macOS arm64, PHP 8.5.9, Composer 2.8.4. Tool versions were pinned to
1.8.4 / 0.9.7 / 4.24.0 respectively, installed separately from the target projects
with plugins and scripts disabled. These are release tests, not tests of master.
The runner generates two local PSR-4 packages: `fixture/direct` requires
`fixture/transitive`. No external application source is used.

| Fixture | Analyser | composer-unused | RequireChecker |
|---|---|---|---|
| Both dependencies explicitly required and used | 0 | 0 | 0 |
| Neither dependency used | 1: unused | 1: unused | 0 |
| Transitive dependency used but not declared | 1: shadow | 0 | 1: unknown symbol |
| Both dependencies in require-dev, used in src | 1: dev in prod | 0 | 1: unknown symbols |
| Both dependencies in require, used only in tests | 1: prod only in dev | 1: unused | 0 |
| Dynamic class name assembled from strings | 1: unused direct | 1: unused direct | 0 |
| Same dynamic use, analyser force-used symbol configured | 0 | 1: unused direct | 0 |
| Additional unknown class | 1: unknown class | 0 | 1: unknown symbol |

Numbers are observed process exit codes, not counts. `composer-unused` reports
production dependencies used only in tests as unused because it does not scan
the test autoload paths by default; this is not the analyser's placement-specific
diagnostic. RequireChecker detects a dev dependency in production through its
absence from `require`, rather than a dedicated placement check. The dynamic
case demonstrates a false positive and a narrow configuration remedy, not a
reason to remove the dependency.

Reproduce with Python 3, PHP and Composer available:

```sh
tools_dir=$(mktemp -d)
COMPOSER_HOME="$tools_dir/home" COMPOSER_CACHE_DIR="$tools_dir/cache" \
  composer require --working-dir="$tools_dir" --no-interaction --no-plugins --no-scripts \
  shipmonk/composer-dependency-analyser:1.8.4 \
  icanhazstring/composer-unused:0.9.7 maglnet/composer-require-checker:4.24.0
python3 research/fixtures/composer-dependencies/run.py --tools "$tools_dir"
```

The [runner](fixtures/composer-dependencies/run.py) prints CSV to stdout and
individual diagnostics to stderr, asserts all exit-code triples, and removes its
temporary projects. Fixture installation uses only local path repositories with
network disabled. The tools' top-level versions are pinned; the separate tool
installation resolves their transitive dependencies for the current PHP runtime.
Retain its generated `composer.lock` when comparing environments. Composer 2.8.4
emitted deprecation notices under PHP 8.5; fixture assertions still passed.

## Integration, configuration and overlap

The [analyser's official README](https://github.com/shipmonk-rnd/composer-dependency-analyser#readme)
documents automatic scanning of `autoload` and `autoload-dev`, PHP-extension
analysis, extra scan paths, force-used symbols, per-package/per-path error ignores
and JUnit output. Its runtime package has no Composer dependencies. Unused dev
dependencies are excluded by default because CLI tools can be used outside PHP
source; opt in explicitly. Our fixtures disabled extension analysis to isolate
package classification. Extensions and JUnit output were read, not executed.

[composer-unused](https://github.com/composer-unused/composer-unused#readme)
provides a focused unused-dependency check, package filters, extra files and
framework configuration sets, including Symfony. Prefer it when that focused
check and its framework integration meet the project's requirements.
[RequireChecker](https://github.com/maglnet/ComposerRequireChecker#readme)
provides a focused undeclared-symbol check, JSON configuration, additional scan
files and a preferred standalone PHAR distribution. Its docs warn about custom
installer layouts. Neither documented workflow modifies dependency declarations
automatically. Configuration capabilities here were read; only the analyser's
force-used symbol configuration was exercised.

[Mago guard](https://github.com/carthage-software/mago/blob/main/docs/content/en/tools/guard/overview.md)
validates allowed edges between application layers and structural conventions.
That intersects with dependency policy at the architectural level, but the
reviewed documentation does not establish automatic reconciliation of Composer
package declarations with production/test symbol usage. Mago's unknown-symbol
analysis can overlap one symptom; it does not make the four hygiene checks in
this comparison redundant. Mago itself was not executed in this experiment.

No comparative speed claim is made. The analyser README's benchmark uses an
unspecified codebase and older comparison versions; it cannot establish an
advantage over the composer-unused release from yesterday.

## Conditions before adoption

Start with installed dependencies, classify production and test paths correctly,
and include entrypoints/configuration that fall outside Composer autoload paths.
Dynamic service registration and config-only references require explicit symbols
or narrowly documented exceptions. Do not globally suppress unused or shadow
errors just to make an initial run green.

The eight fixtures support advancing this candidate: one gate covers the jobs
split across the alternatives and gives placement-specific diagnostics. They do
not validate a real Symfony/Laravel application, Composer plugins, replacement
packages or extension portability. The unreleased master fixes and public false
positive reports remain reasons for a framework trial before a registry pick.

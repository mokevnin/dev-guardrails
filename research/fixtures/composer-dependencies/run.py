#!/usr/bin/env python3
"""Generate local Composer packages and compare three separately installed tools."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--tools', type=Path, required=True, help='Directory containing vendor/bin for the pinned tools')
args = parser.parse_args()
tools = args.tools.resolve() / 'vendor/bin'
env = dict(os.environ, NO_COLOR='1', COMPOSER_DISABLE_NETWORK='1')
for binary, version in [('composer-dependency-analyser', '1.8.4'),
                        ('composer-unused', '0.9.7'),
                        ('composer-require-checker', '4.24.0')]:
    result = subprocess.run([str(tools / binary), '--version'], env=env,
                            check=True, capture_output=True, text=True)
    print(result.stdout.strip(), file=sys.stderr)
    assert version in result.stdout, (binary, result.stdout)

with tempfile.TemporaryDirectory(prefix='dependency-fixtures-') as temporary:
    root = Path(temporary)
    env.update(COMPOSER_HOME=str(root / 'composer-home'), COMPOSER_CACHE_DIR=str(root / 'composer-cache'))
    expected = [(0, 0, 0), (1, 1, 0), (1, 0, 1), (1, 0, 1),
                (1, 1, 0), (1, 1, 0), (0, 1, 0), (1, 0, 1)]
    def write(path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    for package in ['direct', 'transitive']:
        manifest = {'name': 'fixture/' + package, 'version': '1.0.0', 'license': 'MIT',
                    'autoload': {'psr-4': {'Fixture\\' + package.title() + '\\': 'src/'}}}
        if package == 'direct':
            manifest['require'] = {'fixture/transitive': '1.0.0'}
        write(root / 'packages' / package / 'composer.json', json.dumps(manifest))
        write(root / 'packages' / package / 'src/Thing.php',
              '<?php\nnamespace Fixture\\' + package.title() + ';\nclass Thing {}\n')
    scenarios = {
        'clean': ('require', 'src', 'new \\Fixture\\Direct\\Thing(); new \\Fixture\\Transitive\\Thing();', True),
        'unused': ('require', 'src', '', True),
        'shadow': ('require', 'src', 'new \\Fixture\\Direct\\Thing(); new \\Fixture\\Transitive\\Thing();', False),
        'dev-in-prod': ('require-dev', 'src', 'new \\Fixture\\Direct\\Thing(); new \\Fixture\\Transitive\\Thing();', True),
        'prod-only-in-dev': ('require', 'tests', 'new \\Fixture\\Direct\\Thing(); new \\Fixture\\Transitive\\Thing();', True),
        'dynamic-use': ('require', 'src', '$name = "Fixture" . "\\\\Direct\\\\Thing"; new $name(); new \\Fixture\\Transitive\\Thing();', True),
        'dynamic-configured': ('require', 'src', '$name = "Fixture" . "\\\\Direct\\\\Thing"; new $name(); new \\Fixture\\Transitive\\Thing();', True),
        'unknown': ('require', 'src', 'new \\Fixture\\Direct\\Thing(); new \\Fixture\\Transitive\\Thing(); new \\Missing\\Thing();', True),
    }
    print('scenario,analyser,unused,require-checker')
    for name, (section, directory, body, explicit_transitive) in scenarios.items():
        project = root / name
        deps = {'fixture/direct': '1.0.0'}
        if explicit_transitive:
            deps['fixture/transitive'] = '1.0.0'
        manifest = {'name': 'fixture/application', 'license': 'MIT', section: deps,
                    'repositories': [{'type': 'path', 'url': str(root / 'packages/*'), 'options': {'symlink': False}}],
                    'autoload': {'psr-4': {'App\\': 'src/'}},
                    'autoload-dev': {'psr-4': {'AppTests\\': 'tests/'}}}
        write(project / 'composer.json', json.dumps(manifest))
        (project / 'src').mkdir(exist_ok=True)
        (project / 'tests').mkdir(exist_ok=True)
        write(project / 'src/Anchor.php', '<?php\nnamespace App;\nclass Anchor {}\nnew Anchor();\n')
        write(project / directory / 'Example.php', '<?php\n' + body + '\n')
        subprocess.run(['composer', 'update', '--no-interaction', '--no-plugins', '--no-scripts'], cwd=project, env=env, check=True, capture_output=True)
        if name == 'dynamic-configured':
            write(project / 'composer-dependency-analyser.php', '''<?php
return (new \\ShipMonk\\ComposerDependencyAnalyser\\Config\\Configuration())
    ->addForceUsedSymbols(['Fixture\\\\Direct\\\\Thing']);
''')
        commands = [
            [str(tools / 'composer-dependency-analyser'), '--disable-ext-analysis'],
            [str(tools / 'composer-unused'), '--no-progress'],
            [str(tools / 'composer-require-checker'), 'check', 'composer.json'],
        ]
        codes = []
        for index, command in enumerate(commands):
            result = subprocess.run(command, cwd=project, env=env, capture_output=True, text=True)
            codes.append(str(result.returncode))
            print(f'--- {name} tool {index}: exit {result.returncode} ---\n{result.stdout}{result.stderr}', file=sys.stderr)
        print(name + ',' + ','.join(codes))
        assert tuple(map(int, codes)) == expected[list(scenarios).index(name)], (name, codes)

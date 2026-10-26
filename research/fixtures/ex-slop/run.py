#!/usr/bin/env python3
"""Run Credo with the ExSlop plugin on code with typical generated-code slop and on its idiomatic rewrite."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

CREDO, EX_SLOP = '1.7.19', '0.4.5'

SLOP = '''defmodule Slop do
  @moduledoc "This module provides functionality for handling users."

  def parse(id) do
    try do
      String.to_integer(id)
    rescue
      _ -> nil
    end
  end

  def names(users), do: Enum.filter(users, fn u -> u != nil end)

  def none?(xs) when length(xs) == 0, do: true
  def none?(_xs), do: false

  def ranked(xs), do: xs |> Enum.sort() |> Enum.reverse()
end
'''

CLEAN = '''defmodule Clean do
  @moduledoc "Users by name."

  def parse(id) do
    case Integer.parse(id) do
      {n, ""} -> n
      _other -> nil
    end
  end

  def names(users), do: Enum.reject(users, &is_nil/1)

  def none?([]), do: true
  def none?(_xs), do: false

  def ranked(xs), do: Enum.sort(xs, :desc)
end
'''

with tempfile.TemporaryDirectory(prefix='ex-slop-') as temporary:
    root = Path(temporary)
    subprocess.run(['mix', 'new', 'fixture'], cwd=root, check=True, capture_output=True)
    project = root / 'fixture'
    mix = (project / 'mix.exs').read_text().replace(
        '# {:dep_from_hexpm, "~> 0.3.0"},',
        f'{{:credo, "== {CREDO}", only: :dev, runtime: false}}, {{:ex_slop, "== {EX_SLOP}", only: :dev, runtime: false}},')
    (project / 'mix.exs').write_text(mix)
    (project / '.credo.exs').write_text('%{configs: [%{name: "default", plugins: [{ExSlop, []}]}]}\n')
    subprocess.run(['mix', 'deps.get'], cwd=project, check=True, capture_output=True)
    print('file,exit,ex_slop_checks')
    for name, source in [('slop', SLOP), ('clean', CLEAN)]:
        (project / 'lib/fixture.ex').unlink(missing_ok=True)
        for old in (project / 'lib').glob('*.ex'):
            old.unlink()
        (project / 'lib' / f'{name}.ex').write_text(source)
        result = subprocess.run(['mix', 'credo', '--strict', '--format', 'json'],
                                cwd=project, capture_output=True, text=True)
        issues = json.loads(result.stdout[result.stdout.index('{'):])['issues']
        checks = sorted({i['check'].removeprefix('ExSlop.Check.') for i in issues if i['check'].startswith('ExSlop.')})
        print(f'{name},{result.returncode},{" ".join(checks)}')
        print(result.stdout, file=sys.stderr)
        assert (result.returncode != 0) == (name == 'slop'), (name, result.returncode)

#!/usr/bin/env python3
"""What the Elixir compiler's type checks catch, and what only Dialyzer (through Dialyxir) catches: specs that lie."""
from pathlib import Path
import subprocess
import sys
import tempfile
import time

DIALYXIR = '1.4.8'

# caught by `mix compile --warnings-as-errors` (Elixir 1.20): plain type errors, inferred across functions
COMPILER = '''defmodule Fixture do
  def inc(x), do: x + 1
  def wrong_call, do: inc(:not_a_number)
  def plain_type_error, do: :atom + 1
end
'''

# compiles cleanly: the compiler does not read @spec
SPECS = '''defmodule Fixture do
  @spec name() :: integer()
  def name, do: "scav"

  @spec loops() :: :ok
  def loops do
    raise "boom"
    :ok
  end
end
'''

def run(project, *command):
    started = time.monotonic()
    result = subprocess.run(command, cwd=project, capture_output=True, text=True)
    print(f'--- {" ".join(command)}: exit {result.returncode} ---\n{result.stdout}{result.stderr}', file=sys.stderr)
    return result, round(time.monotonic() - started)

with tempfile.TemporaryDirectory(prefix='dialyxir-') as temporary:
    root = Path(temporary)
    subprocess.run(['mix', 'new', 'fixture'], cwd=root, check=True, capture_output=True)
    project = root / 'fixture'
    mix = (project / 'mix.exs').read_text().replace(
        '# {:dep_from_hexpm, "~> 0.3.0"},', f'{{:dialyxir, "== {DIALYXIR}", only: :dev, runtime: false}},')
    (project / 'mix.exs').write_text(mix)
    subprocess.run(['mix', 'deps.get'], cwd=project, check=True, capture_output=True)
    print('step,exit,seconds,found')

    (project / 'lib/fixture.ex').write_text(COMPILER)
    result, seconds = run(project, 'mix', 'compile', '--warnings-as-errors', '--force')
    found = [f for f in ['wrong_call', 'plain_type_error'] if f'Fixture.{f}' in result.stdout + result.stderr]
    print(f'compile type errors,{result.returncode},{seconds},{" ".join(found)}')
    assert result.returncode != 0 and len(found) == 2

    (project / 'lib/fixture.ex').write_text(SPECS)
    result, seconds = run(project, 'mix', 'compile', '--warnings-as-errors', '--force')
    print(f'compile lying specs,{result.returncode},{seconds},')
    assert result.returncode == 0

    for step in ['dialyzer first run', 'dialyzer second run']:
        result, seconds = run(project, 'mix', 'dialyzer', '--format', 'short')
        found = sorted({w for w in ['invalid_contract', 'no_return'] if w in result.stdout + result.stderr})
        print(f'{step},{result.returncode},{seconds},{" ".join(found)}')
        assert result.returncode == 2 and found == ['invalid_contract', 'no_return']

your5e
======

A set of tools to help with running fifth edition D&D.


## Rules parsing and directives

Rules are expected to be [written up](rules/README.md) including special
directives to explain to both the players and the tools.

Rules files can be checked for invalid directives:

```bash
# find errors
your5e check-rules rules/directives/hit_die.md

# successful directives also...
your5e check-rules --verbose rules/directives/hit_die.md
```


## Developing `your5e`

Requires:

- Python 3.10+
    - `pip install -e .[dev]`
- [bats](https://github.com/bats-core/bats-core) for CLI testing
    - `brew install bats-core` (on macOS)

Run black reformatting, flake8 linting, python, and CLI tests:

```bash
make test           # everything

make format         # black
make lint           # flake8
make tests          # both of:
make tests-python   #   pytest
make tests-bats     #   bats
```

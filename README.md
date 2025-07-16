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

## Development

Requires:

- Python 3.9+
- [bats](https://github.com/bats-core/bats-core) for CLI testing (install with `brew install bats-core` on macOS)

Install development dependencies:

```bash
pip install -e .[dev]
```

Run black reformatting, flake8 linting, python, and CLI tests:

```bash
make test
```

Or individually:

- `make format` — black
- `make lint` — flake8
- `make tests-python` — pytest
- `make tests-bats` — bats

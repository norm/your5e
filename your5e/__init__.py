import sys


if sys.version_info < (3, 10):
    print("Error: requires python 3.10 or higher.", file=sys.stderr)
    sys.exit(2)

__version__ = "0.1.0"

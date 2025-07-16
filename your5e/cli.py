import argparse
import sys
from typing import List, Optional

from .commands.check_rules import CheckRulesCommand


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="your5e", description="A D&D 5e rules parser and utility tool"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    CheckRulesCommand.add_parser(subparsers)

    return parser


def main(args: Optional[List[str]] = None) -> int:
    parser = create_parser()

    if args is None:
        args = sys.argv[1:]

    parsed_args = parser.parse_args(args)
    if not parsed_args.command:
        parser.print_help()
        return 1

    if parsed_args.command == "check-rules":
        return CheckRulesCommand.run(parsed_args)

    print(f"Unknown command: {parsed_args.command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())

import argparse
import os
import sys

from ..rules import RuleParser


class CheckRulesCommand:
    @classmethod
    def add_parser(cls, subparsers) -> argparse.ArgumentParser:
        parser = subparsers.add_parser(
            "check-rules",
            help="Check rules files for parsing errors",
        )
        parser.add_argument(
            "files",
            nargs="+",
            help="Rules files to check",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Also report successful directives",
        )
        return parser

    @classmethod
    def run(cls, args: argparse.Namespace) -> int:
        exit_code = 0
        context_lines = 2

        for file in args.files:
            if file == "-":  # read from stdin
                content = sys.stdin.read()
                file = "<stdin>"
                print()
            else:
                if not os.path.exists(file):
                    print(f"Error: '{file}' not found")
                    exit_code = 1
                    continue
                try:
                    with open(file, "r") as f:
                        content = f.read()
                except Exception as e:
                    print(f"Error reading file '{file}': {e}")
                    exit_code = 1
                    continue

            result_objects, errors = RuleParser().parse_rules(content)

            if errors or args.verbose:
                print(f"{file}: {len(errors)} errors")
            if args.verbose and len(result_objects):
                total_directives = len(result_objects)
                print(f"+ {total_directives} directives:")

                for directive in result_objects:
                    print(f"        {directive}")

                if errors:
                    print()

            if errors:
                exit_code = 1
                content_lines = content.split("\n")
                lines = "", *content_lines

                error_lines = {error["line"] for error in errors}
                error_groups = []
                current_group = []

                for error in sorted(errors, key=lambda e: e["line"]):
                    if (
                        not current_group
                        or error["line"] - current_group[-1]["line"] <= context_lines
                    ):
                        current_group.append(error)
                    else:
                        error_groups.append(current_group)
                        current_group = [error]

                if current_group:
                    error_groups.append(current_group)

                for count, group in enumerate(error_groups):
                    # errors grouped before context lines
                    for error in group:
                        line = error["line"]
                        print(f"- {line}: {error['text']}")

                    if content_lines:
                        start_line = max(
                            0, min(error["line"] for error in group) - context_lines
                        )
                        end_line = min(
                            len(lines) - 1,
                            max(error["line"] for error in group) + context_lines,
                        )

                        for line in range(start_line, end_line + 1):
                            if line < len(lines):
                                marker = ">" if line in error_lines else " "
                                print(f"    {marker:2s} {line:4d}: {lines[line]}")

                    if count < len(error_groups) - 1:
                        print()

                if len(args.files) > 1:
                    print()

        return exit_code

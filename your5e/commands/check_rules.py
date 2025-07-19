import argparse
import sys
from pathlib import Path

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
            help="Rules files or directories to check",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Also report successful directives",
        )
        parser.add_argument(
            "--context",
            type=int,
            default=0,
            help="Number of lines of context to show around errors (default: 0)",
        )
        return parser

    @classmethod
    def run(cls, args: argparse.Namespace) -> int:
        exit_code = 0

        if args.files[0] == "-":
            content = sys.stdin.read()
            return cls.validate_content("<stdin>", content, args.verbose, args.context)

        found_files = []
        for path_str in args.files:
            if path_str == "-":
                # silently ignore if it appears after files
                continue

            path = Path(path_str)
            if not path.exists():
                print(f"Error: '{path_str}' not found")
                continue

            if path.is_file():
                found_files.append(str(path))
            elif path.is_dir():
                md_files = list(path.rglob("*.md"))
                found_files.extend(str(f) for f in sorted(md_files))

        if not found_files:
            return 1

        for count, file in enumerate(found_files):
            try:
                with open(file, "r") as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading file '{file}': {e}")
                exit_code = 1
                continue

            file_exit_code = cls.validate_content(
                file, content, args.verbose, args.context
            )
            if file_exit_code != 0:
                exit_code = file_exit_code

            # space out between multiple files
            if count < len(found_files) - 1 and file_exit_code != 0:
                print()

        return exit_code

    @classmethod
    def validate_content(cls, filename, content, verbose, lines_of_context):
        result_objects, errors = RuleParser().parse_rules(content)

        if errors or verbose:
            print(f"{filename}: {len(errors)} errors")
        if verbose and len(result_objects):
            total_directives = len(result_objects)
            print(f"  + {total_directives} directives found:")

            for directive in result_objects:
                print(f"          {directive}")

            if errors:
                print()

        if not errors:
            return 0

        content_lines = content.split("\n")
        lines = "", *content_lines
        errors_grouped = []
        current_group = []

        for error in sorted(errors, key=lambda e: e["line"]):
            if (
                not current_group
                or error["line"] - current_group[-1]["line"] <= lines_of_context
            ):
                current_group.append(error)
            else:
                errors_grouped.append(current_group)
                current_group = [error]

        if current_group:
            errors_grouped.append(current_group)

        for count, group in enumerate(errors_grouped):
            group_error_lines = set()

            # errors are grouped in the output before context
            # lines are shown where they overlap
            for error in group:
                line = error["line"]
                print(f"  - {line}: {error['text']}")
                if lines_of_context > 0:
                    group_error_lines.add(line)

            if content_lines and lines_of_context > 0:
                start_line = max(0, group[0]["line"] - lines_of_context)
                end_line = min(len(lines) - 1, group[-1]["line"] + lines_of_context)

                for line in range(start_line, end_line + 1):
                    marker = ">" if line in group_error_lines else " "
                    print(f"      {marker:2s} {line:4d}: {lines[line]}")

                if count < len(errors_grouped) - 1:
                    print()

        return 1

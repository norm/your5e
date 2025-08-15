from typing import Dict, List, Any, Tuple
import inspect
import re

from .directives import DIRECTIVES


def extract_key_value(text: str):
    # "- _key_ value..." -> (key, value...)
    if text.startswith("- "):
        text = text[2:].strip()
        try:
            key, value = text.split(None, 1)
        except ValueError:
            key = text
            value = ""

        for marker in ["**", "__", "*", "_"]:
            if key.startswith(marker) and key.endswith(marker):
                if key[len(marker) : -len(marker)]:
                    return (key[len(marker) : -len(marker)].lower(), value)
                return None
    return None


SHORTHAND_FORMAT = re.compile(
    r"""
        ^
        (?P<directive> \w+ (?: \s+ \w+ )* )
        \s+
        (?P<marker> \*\* | __ | [*_] )  # opening emphasis
        (?P<key> \w+ (?: \s+ \w+ )* )
        (?P=marker)                     # closing marker
        (?: \s+ (?P<value> .+ ))?       # value (optional)
    """,
    re.VERBOSE,
)


class DirectivePosition:
    def directive_position(self, lines: List[str], line: int) -> bool:
        """
        The only places in a Markdown file considered valid for directives to
        appear are at the very start of the file, or immediately after a header.
        Blank lines are acceptable, any other text terminates.
        """
        if line == 0:
            return True

        # look backwards to check the block starts correctly
        for index in range(line, -1, -1):
            prev_line = lines[index].strip()
            if prev_line:
                if prev_line.startswith("#"):
                    return True
                if prev_line.startswith("- "):
                    continue
                return False

        return True

    def next_directive_block(
        self, lines: List[str], index: int
    ) -> Tuple[int, List[str]] | None:
        while index < len(lines):
            line = lines[index]

            if not line.startswith("- ") or not self.directive_position(lines, index):
                index += 1
                continue

            directive_name = line[2:].strip().lower()
            if directive_name.startswith("comment") or directive_name.startswith("#"):
                index += 1
                continue

            start_index = index
            index += 1

            while index < len(lines):
                line = lines[index]
                stripped = line.strip()

                if (
                    # block ends on blank lines,
                    stripped == ""
                    # a new directive,
                    or line.startswith("- ")
                    # or any non-argument text
                    or not stripped.startswith("- ")
                ):
                    break

                index += 1

            return (
                start_index,
                lines[start_index:index],
            )

        return None


class RuleParser(DirectivePosition):
    def parse_rules(
        self,
        content: str,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        result = []
        errors = []
        lines = content.split("\n")

        last_index = 0
        while True:
            block_info = self.next_directive_block(lines, last_index)
            if block_info is None:
                break

            index, block_lines = block_info
            last_index = index + len(block_lines)
            directive = block_lines[0][2:].strip()
            parse_error = False
            line_number = index + 1

            shorthand_match = SHORTHAND_FORMAT.match(directive)
            if shorthand_match:
                directive = shorthand_match.group("directive")
                key = shorthand_match.group("key")
                value = shorthand_match.group("value") or ""

            directive_info = DIRECTIVES.get(directive.lower())
            if not directive_info:
                errors.append(
                    {
                        "line": line_number,
                        "text": f"Unknown directive: {directive}",
                    }
                )
                continue

            directive_class = directive_info["class"]

            # check for a directive that supports nested directives (eg Choose)
            sig = inspect.signature(directive_class.new)
            wants_content = "raw_lines" in sig.parameters

            args = {}
            if shorthand_match:
                # shorthand is formatted key/value, but the key might not be
                # "key" and value might not be "value"" (eg Resource fills in
                # the "name" and "uses" keys for its shorthand)
                shorthand_key = getattr(directive_info["class"], "SHORTHAND_KEY", "key")
                shorthand_value = getattr(
                    directive_info["class"], "SHORTHAND_VALUE", "value"
                )

                args = {shorthand_key: {"value": key, "line": line_number}}
                if value:
                    args[shorthand_value] = {"value": value, "line": line_number}

            if wants_content:
                directive_obj, invalid = directive_class.new(
                    line_number, args, raw_lines=block_lines
                )
            else:
                if shorthand_match and len(block_lines) > 1:
                    if any(
                        line
                        and not line.startswith("- #")
                        and not line.lower().startswith("- comment")
                        for line in (line.strip() for line in block_lines[1:])
                    ):
                        errors.append(
                            {
                                "line": line_number,
                                "text": "No arguments when using shorthand notation.",
                            }
                        )
                        parse_error = True
                elif not shorthand_match:
                    for count, line in enumerate(block_lines[1:], 1):
                        key_value_pair = extract_key_value(line.strip())
                        if key_value_pair:
                            key, value = key_value_pair
                        else:
                            errors.append(
                                {
                                    "line": line_number + count,
                                    "text": "Argument has no key.",
                                }
                            )
                            parse_error = True
                            continue

                        # last occurence wins
                        args[key] = {"value": value, "line": line_number + count}

                directive_obj, invalid = directive_class.new(line_number, args)

            if parse_error or invalid:
                errors.extend(invalid)
            else:
                result.append(directive_obj)

        return result, sorted(errors, key=lambda e: e["line"])

    def parse_rules_file(
        self,
        file_path: str,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        with open(file_path, "r") as f:
            content = f.read()
        return self.parse_rules(content)


class DirectiveExtract(DirectivePosition):
    def extract(self, markdown_content: str) -> Tuple[str, str]:
        lines = markdown_content.split("\n")
        markdown_lines = []
        directive_lines = []
        last_index = 0

        while True:
            block_info = self.next_directive_block(lines, last_index)
            if block_info is None:
                break

            index, block_lines = block_info
            directive_lines.extend(block_lines)

            # any blank lines between a header and the end of the
            # directives are not to be copied
            section_start = 0
            for lookback in range(index, -1, -1):
                if lines[lookback].strip().startswith("#"):
                    section_start = lookback
                    break
            for copy in range(last_index, index):
                line = lines[copy]
                if section_start <= copy and line.strip() == "":
                    continue
                markdown_lines.append(line)

            last_index = index + len(block_lines)

        # remaining lines
        markdown_lines.extend(lines[last_index:])

        markdown = "\n".join(markdown_lines)
        if markdown and not markdown.endswith("\n"):
            markdown += "\n"

        directives = "\n".join(directive_lines)
        if directives and not directives.endswith("\n"):
            directives += "\n"

        return markdown, directives

    def extract_file(self, file_path: str) -> Tuple[str, str]:
        with open(file_path, "r") as f:
            content = f.read()
        return self.extract(content)

from typing import Dict, List, Any, Tuple

from .directives import DIRECTIVES


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
            directive_info = DIRECTIVES.get(directive.lower())
            if not directive_info:
                errors.append(
                    {
                        "line": index + 1,
                        "text": f"Unknown directive: {directive}",
                    }
                )
                continue

            directive_class = directive_info["class"]

            args = {}
            parse_error = False
            for count, line in enumerate(block_lines[1:], 1):
                try:
                    (first_word, value) = line.strip()[2:].split(None, 1)
                except ValueError:
                    first_word = line.strip()[2:]
                    value = ""

                key = None
                for marker in ["**", "__", "*", "_"]:
                    if first_word.startswith(marker) and first_word.endswith(marker):
                        key = first_word[len(marker) : -len(marker)].lower()
                        break

                if not key:
                    errors.append(
                        {
                            "line": index + count + 1,
                            "text": "Argument has no key.",
                        }
                    )
                    parse_error = True
                    continue

                # last occurence wins
                args[key] = {"value": value, "line": index + count + 1}

            directive_obj, invalid = directive_class.new(index, args)
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

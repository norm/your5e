from dataclasses import dataclass
from typing import Optional, List
import textwrap

from . import Directive


@dataclass
class ChooseOption:
    name: str
    directives: List[Directive]


@dataclass
class Choose(Directive):
    DIRECTIVE_NAME = "Choose"
    DIRECTIVE_KEY = "choose"
    SHORTHAND_KEY = "count"
    SHORTHAND_VALUE = "name"

    count: int = 0
    description: Optional[str] = None
    options: List[ChooseOption] = None

    def __post_init__(self):
        if self.options is None:
            self.options = []

    @classmethod
    def new(
        cls,
        line: int,
        args: dict,
        raw_lines: Optional[List[str]] = None,
    ) -> tuple[Optional["Choose"], list]:
        directive_args, options_start_index = get_arguments(
            raw_lines[1:],
            line,
        )
        args.update(directive_args)

        # required arguments
        if "count" not in args or not args["count"]["value"]:
            return None, [
                {
                    "line": line,
                    "text": 'Required "count" argument is missing.',
                }
            ]
        try:
            args["count"]["value"] = int(args["count"]["value"])
            if args["count"]["value"] < 1:
                raise ValueError()
        except ValueError:
            return None, [
                {
                    "line": args["count"]["line"],
                    "text": (
                        f'Count "{args["count"]["value"]}" should be a '
                        "positive integer."
                    ),
                }
            ]

        options, option_errors = get_options(
            raw_lines[options_start_index:], line + options_start_index
        )
        if option_errors:
            return None, option_errors
        if len(options) < args["count"]["value"]:
            return None, [
                {
                    "line": line,
                    "text": "Not enough options to choose from.",
                }
            ]
        obj = cls.create_object(args, line)
        obj.options = options
        return obj, []

    def _transform_dict(self, data: dict) -> dict:
        if "options" in data and data["options"]:
            options_dicts = []
            for option in data["options"]:
                if isinstance(option, ChooseOption):
                    option_dict = {
                        "name": option.name,
                        "directives": [
                            directive.asdict() for directive in option.directives
                        ],
                    }
                else:
                    option_dict = option
                options_dicts.append(option_dict)
            data["options"] = options_dicts
        return data

    def to_markdown(self) -> str:
        """Convert Choose directive back to Markdown format."""
        # Determine if we can use shorthand
        can_use_shorthand = (
            self.name is not None and self.description is None and self.comment is None
        )

        lines = []

        if can_use_shorthand:
            # Shorthand format: - Choose _count_ name
            lines.append(f"- Choose _{self.count}_ {self.name}")
        else:
            # Full format
            if self.name is None:
                # Special case: no name but has count
                lines.append(f"- Choose _{self.count}_")
            else:
                lines.append("- Choose")
                # Add directive-specific fields first
                lines.append(f"    - _Count_ {self.count}")
                if self.name is not None:
                    lines.append(f"    - _Name_ {self.name}")
                if self.description is not None:
                    lines.append(f"    - _Description_ {self.description}")

        # Add options
        for option in self.options:
            lines.append(f"    - _Option_ {option.name}")
            for directive in option.directives:
                directive_markdown = directive.to_markdown()
                # Indent each line of the directive by 8 spaces
                for line in directive_markdown.strip().split("\n"):
                    lines.append(f"        {line}")

        return "\n".join(lines) + "\n"

    def __str__(self) -> str:
        name_part = f"{self.name} " if self.name else ""
        return (
            f"{self.DIRECTIVE_NAME}: {name_part}({self.count} from "
            f"{len(self.options)} options)"
        )


def get_arguments(lines: List[str], line_number: int) -> tuple[dict, int]:
    from .. import extract_key_value

    args = {}
    for index, line in enumerate(lines):
        kv = extract_key_value(line.strip())
        if kv and kv[0] == "option":
            return args, index + 1
        elif kv:
            args[kv[0]] = {"line": index, "value": kv[1]}

    # no options found
    return args, len(lines)


def get_options(lines: List[str], base_line: int) -> tuple[List[ChooseOption], list]:
    from .. import RuleParser, extract_key_value

    parser = RuleParser()
    options = []
    errors = []
    index = 0

    # dedent the lines for next_directive_block to work
    lines = textwrap.dedent("\n".join(lines)).split("\n")

    while index < len(lines):
        actual_line = base_line + index
        line = lines[index]
        kv = extract_key_value(line)
        if kv and kv[0] == "option":
            block_index, block_lines = parser.next_directive_block(lines, index)
            directives, directive_errors = parser.parse_rules(
                # dedent the lines for next_directive_block to work
                textwrap.dedent("\n".join(block_lines[1:]))
            )
            if directive_errors:
                errors.extend(directive_errors)
            elif not directives:
                errors.append(
                    {
                        "line": actual_line,
                        "text": ("Option must contain at least one directive."),
                    }
                )
            else:
                options.append(ChooseOption(name=kv[1], directives=directives))

            index = block_index + len(block_lines)
        else:
            index += 1
            if len(options):
                if kv:
                    errors.append(
                        {
                            "line": actual_line,
                            "text": "Arguments come before options.",
                        }
                    )
                elif line.strip().startswith("- "):
                    errors.append(
                        {
                            "line": actual_line,
                            "text": "Directives must be inside option.",
                        }
                    )

    return options, errors

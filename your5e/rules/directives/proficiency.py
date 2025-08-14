from dataclasses import dataclass
from typing import Optional

from . import Directive


@dataclass
class Proficiency(Directive):
    DIRECTIVE_NAME = "Proficiency"
    DIRECTIVE_KEY = "proficiency"
    SHORTHAND_KEY = "type"

    type: str = ""
    value: str = ""

    @classmethod
    def new(
        cls,
        line: int,
        args: dict,
    ) -> tuple[Optional["Proficiency"], list]:
        # required arguments
        errors = []
        if "type" not in args or not args["type"]["value"]:
            errors.append(
                {
                    "line": line,
                    "text": 'Required "type" argument is missing.',
                }
            )
        if "value" not in args or not args["value"]["value"]:
            errors.append(
                {
                    "line": line,
                    "text": 'Required "value" argument is missing.',
                }
            )
        if errors:
            return None, errors

        # validate type
        proficiency_types = [
            "armor",
            "initiative",
            "saving throw",
            "skill",
            "tool",
            "weapon",
        ]
        if args["type"]["value"].lower() not in proficiency_types:
            return None, [
                {
                    "line": args["type"]["line"],
                    "text": f'Type "{args["type"]["value"]}" should be either '
                    f'{", ".join(proficiency_types)}.',
                }
            ]

        return cls.create_object(args, line), []

    def _transform_dict(self, data: dict) -> dict:
        if "type" in data:
            data["type"] = data["type"].lower()
        return data

    def __str__(self) -> str:
        return f"{self.DIRECTIVE_NAME}: {self.type} {self.value}"

from dataclasses import dataclass
from typing import Optional

from . import Directive


@dataclass
class Register(Directive):
    DIRECTIVE_NAME = "Register"
    DIRECTIVE_KEY = "register"
    SHORTHAND_KEY = "type"
    SHORTHAND_VALUE = "name"

    type: str = ""

    @classmethod
    def new(
        cls,
        line: int,
        args: dict,
    ) -> tuple[Optional["Register"], list]:
        errors = []
        if "type" not in args or not args["type"]["value"]:
            errors.append(
                {
                    "line": line,
                    "text": 'Required "type" argument is missing.',
                }
            )
        if "name" not in args or not args["name"]["value"]:
            errors.append(
                {
                    "line": line,
                    "text": 'Required "name" argument is missing.',
                }
            )
        if errors:
            return None, errors

        if "type" in args:
            valid_types = ["Ability Score", "Roll", "Skill"]
            type_value = args["type"]["value"]
            normalized_type = cls._normalize_type(type_value)
            if normalized_type not in valid_types:
                return None, [
                    {
                        "line": args["type"]["line"],
                        "text": f'Type "{type_value}" should be either '
                        f'{", ".join(valid_types)}.',
                    }
                ]

        return cls.create_object(args, line), []

    @staticmethod
    def _normalize_type(type_value: str) -> str:
        type_mapping = {
            "ability score": "Ability Score",
            "roll": "Roll",
            "skill": "Skill",
        }
        return type_mapping.get(type_value.lower(), type_value)

    def _transform_dict(self, data: dict) -> dict:
        if "type" in data and data["type"]:
            data["type"] = self._normalize_type(data["type"])
        return data

    def __str__(self) -> str:
        return f"{self.DIRECTIVE_NAME}: {self.name} ({self.type})"

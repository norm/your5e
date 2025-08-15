from dataclasses import dataclass
from typing import Optional

from . import Directive


@dataclass
class Set(Directive):
    DIRECTIVE_NAME = "Set"
    DIRECTIVE_KEY = "set"

    key: str = ""
    value: str = ""

    @classmethod
    def new(
        cls,
        line: int,
        args: dict,
    ) -> tuple[Optional["Set"], list]:
        # required arguments
        errors = []
        if "key" not in args or not args["key"]["value"]:
            errors.append(
                {
                    "line": line,
                    "text": 'Required "key" argument is missing.',
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

        return cls.create_object(args, line), []

    def __str__(self) -> str:
        return f"{self.DIRECTIVE_NAME}: {self.key} = '{self.value}'"

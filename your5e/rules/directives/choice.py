from dataclasses import dataclass
from typing import Optional

from . import Directive


@dataclass
class Choice(Directive):
    DIRECTIVE_NAME = "Choice"
    DIRECTIVE_KEY = "choice"
    SHORTHAND_KEY = "name"
    SHORTHAND_VALUE = "choice"

    choice: str = ""

    @classmethod
    def new(
        cls,
        line: int,
        args: dict,
    ) -> tuple[Optional["Choice"], list]:
        # required arguments
        errors = []
        if "name" not in args or not args["name"]["value"]:
            errors.append(
                {
                    "line": line,
                    "text": 'Required "name" argument is missing.',
                }
            )
        if "choice" not in args or not args["choice"]["value"]:
            errors.append(
                {
                    "line": line,
                    "text": 'Required "choice" argument is missing.',
                }
            )
        if errors:
            return None, errors

        return cls.create_object(args, line), []

    def __str__(self) -> str:
        return f"{self.DIRECTIVE_NAME}: {self.name} ({self.choice})"

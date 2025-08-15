from dataclasses import dataclass
from typing import Optional

from . import Directive


@dataclass
class Language(Directive):
    DIRECTIVE_NAME = "Language"
    DIRECTIVE_KEY = "language"
    SHORTHAND_KEY = "name"

    name: str = ""

    @classmethod
    def new(
        cls,
        line: int,
        args: dict,
    ) -> tuple[Optional["Language"], list]:
        # required arguments
        if "name" not in args or not args["name"]["value"]:
            return None, [
                {
                    "line": line,
                    "text": 'Required "name" argument is missing.',
                }
            ]

        return cls.create_object(args, line), []

    def __str__(self) -> str:
        return f"{self.DIRECTIVE_NAME}: {self.name}"

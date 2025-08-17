from dataclasses import dataclass
from typing import Optional

from . import Directive


@dataclass
class Featureless(Directive):
    DIRECTIVE_NAME = "Featureless"
    DIRECTIVE_KEY = "featureless"

    @classmethod
    def new(
        cls,
        line: int,
        args: dict,
    ) -> tuple[Optional["Featureless"], list]:
        return cls.create_object(args, line), []

    def __str__(self) -> str:
        return f"{self.DIRECTIVE_NAME}"

    def to_markdown(self) -> str:
        return "- Featureless\n"

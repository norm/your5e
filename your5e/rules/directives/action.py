from dataclasses import dataclass
from typing import Optional

from . import Directive


@dataclass
class BaseAction(Directive):
    name: str = ""
    description: str = ""
    uses: Optional[str] = None
    effect: Optional[str] = None
    amount: Optional[str] = None
    roll: Optional[str] = None

    @classmethod
    def new(
        cls,
        line: int,
        args: dict,
    ) -> tuple[Optional["BaseAction"], list]:
        # required arguments
        errors = []
        if "name" not in args or not args["name"]["value"]:
            errors.append(
                {
                    "line": line,
                    "text": 'Required "name" argument is missing.',
                }
            )
        if "description" not in args or not args["description"]["value"]:
            errors.append(
                {
                    "line": line,
                    "text": 'Required "description" argument is missing.',
                }
            )
        if errors:
            return None, errors

        return cls.create_object(args, line), []

    def __str__(self) -> str:
        return f"{self.DIRECTIVE_NAME}: {self.name}"


@dataclass
class Action(BaseAction):
    DIRECTIVE_NAME = "Action"
    DIRECTIVE_KEY = "action"


@dataclass
class BonusAction(BaseAction):
    DIRECTIVE_NAME = "Bonus Action"
    DIRECTIVE_KEY = "bonus_action"


@dataclass
class Reaction(BaseAction):
    DIRECTIVE_NAME = "Reaction"
    DIRECTIVE_KEY = "reaction"

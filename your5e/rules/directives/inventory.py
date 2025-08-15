from dataclasses import dataclass
from typing import Optional

from . import Directive


@dataclass
class Inventory(Directive):
    DIRECTIVE_NAME = "Inventory"
    DIRECTIVE_KEY = "inventory"
    SHORTHAND_KEY = "action"
    SHORTHAND_VALUE = "item"

    action: str = ""
    item: str = ""
    count: Optional[int] = None

    @classmethod
    def new(
        cls,
        line: int,
        args: dict,
    ) -> tuple[Optional["Inventory"], list]:
        # required arguments
        errors = []
        if "action" not in args or not args["action"]["value"]:
            errors.append(
                {
                    "line": line,
                    "text": 'Required "action" argument is missing.',
                }
            )
        if "item" not in args or not args["item"]["value"]:
            errors.append(
                {
                    "line": line,
                    "text": 'Required "item" argument is missing.',
                }
            )
        if errors:
            return None, errors

        # validate action
        if args["action"]["value"].lower() not in ["add", "remove"]:
            return None, [
                {
                    "line": args["action"]["line"],
                    "text": 'Action is either "add" or "remove".',
                }
            ]

        if "count" in args:
            try:
                count_value = int(args["count"]["value"])
            except ValueError:
                count_value = 0
            if count_value < 1:
                return None, [
                    {
                        "line": args["count"]["line"],
                        "text": f'Count "{args["count"]["value"]}" '
                        "should be a positive integer.",
                    }
                ]

            args["count"]["value"] = count_value

        return cls.create_object(args, line), []

    def __str__(self) -> str:
        count_str = f" ({self.count})" if self.count else ""
        return f"{self.DIRECTIVE_NAME}: {self.action} {self.item}{count_str}"

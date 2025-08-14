from dataclasses import dataclass
from typing import Optional

from . import Directive


@dataclass
class Resource(Directive):
    DIRECTIVE_NAME = "Resource"
    DIRECTIVE_KEY = "resource"
    SHORTHAND_KEY = "name"
    SHORTHAND_VALUE = "uses"

    name: str = ""
    uses: str = ""
    renew: Optional[str] = None
    regain: Optional[str] = None

    @classmethod
    def new(
        cls,
        line: int,
        args: dict,
    ) -> tuple[Optional["Resource"], list]:
        # required arguments
        errors = []
        if "name" not in args or not args["name"]["value"]:
            errors.append(
                {
                    "line": line,
                    "text": 'Required "name" argument is missing.',
                }
            )
        if "uses" not in args or not args["uses"]["value"]:
            errors.append(
                {
                    "line": line,
                    "text": 'Required "uses" argument is missing.',
                }
            )
        if errors:
            return None, errors

        # validate renew value
        if "renew" in args:
            renew_periods = ["rest", "long rest", "dawn"]
            if args["renew"]["value"].lower() not in renew_periods:
                return None, [
                    {
                        "line": args["renew"]["line"],
                        "text": f'Renew "{args["renew"]["value"]}" should be either '
                        f'{", ".join(renew_periods)}.',
                    }
                ]

        return cls.create_object(args, line), []

    def _transform_dict(self, data: dict) -> dict:
        if "renew" in data and data["renew"]:
            data["renew"] = data["renew"].lower()
        return data

    def __str__(self) -> str:
        return f"{self.DIRECTIVE_NAME}: {self.name} ({self.uses})"

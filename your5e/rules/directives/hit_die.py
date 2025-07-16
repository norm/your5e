from dataclasses import dataclass
from typing import Optional

from . import Directive


@dataclass
class HitDie(Directive):
    DIRECTIVE_NAME = "Hit Die"
    DIRECTIVE_KEY = "hit_die"

    die: int = 0
    value: Optional[int] = None

    @classmethod
    def new(
        cls,
        index: int,
        args: dict,
    ) -> tuple[Optional["HitDie"], list]:

        index += 1  # 0-indexed

        # required arguments
        if "die" not in args:
            return None, [
                {
                    "line": index,
                    "text": 'Required "die" argument is missing.',
                }
            ]

        # valid die?
        die_value = args["die"]["value"]
        try:
            if not die_value.lower().startswith("d"):
                raise ValueError
            parsed_die = int(die_value[1:])
        except ValueError:
            return None, [
                {
                    "line": args["die"]["line"],
                    "text": f'Die "{die_value}" is not a die.',
                }
            ]

        # only polyhedrals
        if parsed_die not in {4, 6, 8, 10, 12, 20}:
            return None, [
                {
                    "line": args["die"]["line"],
                    "text": f'Die "d{parsed_die}" is not a standard die.',
                }
            ]
        args["die"]["value"] = parsed_die

        # valid value?
        if "value" in args:
            value_str = args["value"]["value"]
            try:
                parsed_value = int(value_str)
                args["value"]["value"] = parsed_value
            except ValueError:
                return None, [
                    {
                        "line": args["value"]["line"],
                        "text": f'Value "{value_str}" is not a number.',
                    }
                ]
            if parsed_value < 1 or parsed_value > args["die"]["value"]:
                return None, [
                    {
                        "line": args["value"]["line"],
                        "text": f'Value "{parsed_value}" is out of range.',
                    }
                ]
        else:
            args["value"] = {
                "value": (args["die"]["value"] // 2) + 1,
                "line": args["die"]["line"],
            }

        return cls.create_object(args, index), []

    def __str__(self) -> str:
        return f"{self.DIRECTIVE_NAME}, d{self.die}, value {self.value}"

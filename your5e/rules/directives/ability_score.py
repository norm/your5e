from dataclasses import dataclass
from typing import Optional
import re

from . import Directive


VALUE_FORMAT = re.compile(
    r"""
        # strict formatting for values: "15", "+2", "-1"
        ^
        (?P<sign>    [+-] )?
        (?P<number>  \d+ )
        $
    """,
    re.VERBOSE,
)
OVERRIDE_FORMAT = re.compile(
    r"""
        # strict formatting for override arguments:
        # "16", "+1", "minimum 19", "+2, maximum 20"
        ^
        (?:
            (?:
                (?P<modifier_sign>  [+-] )?
                (?P<value>          \d+ )
                (?:                 , \s* )?
            )
        )?
        (?:
            (?P<constraint>        minimum | maximum )
                                   \s+
            (?P<constraint_value>  \d+ )
        )?
        $
    """,
    re.VERBOSE | re.IGNORECASE,
)


@dataclass
class AbilityScore(Directive):
    DIRECTIVE_NAME = "Ability Score"
    DIRECTIVE_KEY = "ability_score"
    SHORTHAND_KEY = "ability"

    ability: str = ""
    value: Optional[str] = None
    override: Optional[str] = None
    minimum: Optional[str] = None
    maximum: Optional[str] = None

    @classmethod
    def new(
        cls,
        line: int,
        args: dict,
    ) -> tuple[Optional["AbilityScore"], list]:
        # required arguments
        if "ability" not in args:
            return None, [
                {
                    "line": line,
                    "text": 'Required "ability" argument is missing.',
                }
            ]

        # valid ability?
        ability_value = args["ability"]["value"]
        valid_abilities = {
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        }
        if ability_value.lower() not in valid_abilities:
            return None, [
                {
                    "line": args["ability"]["line"],
                    "text": f'"{ability_value}" is not an ability.',
                }
            ]
        args["ability"]["value"] = ability_value.lower()

        # one or t'other, not both
        has_value = "value" in args
        has_override = "override" in args
        if not has_value and not has_override:
            return None, [
                {
                    "line": line,
                    "text": 'Either "value" or "override" must be specified.',
                }
            ]
        if has_value and has_override:
            return None, [
                {
                    "line": line,
                    "text": 'Only one of "value" and "override" can be specified.',
                }
            ]

        if has_value:
            value = args["value"]["value"]
            match = VALUE_FORMAT.match(value)
            if not match:
                return None, [
                    {
                        "line": args["value"]["line"],
                        "text": f'Value "{value}" is not a valid score or ' "modifier.",
                    }
                ]

            if match.group("sign") == "+":
                args["maximum"] = {"value": "20", "line": args["value"]["line"]}
            elif match.group("sign") == "-":
                args["minimum"] = {"value": "1", "line": args["value"]["line"]}
            else:
                # 3-18 are the only possibilities for rolled abilities
                value = int(match.group("number"))
                if value < 3 or value > 18:
                    return None, [
                        {
                            "line": args["value"]["line"],
                            "text": f'Value "{value}" is out of range (3-18).',
                        }
                    ]

        if has_override:
            override = args["override"]["value"]
            match = OVERRIDE_FORMAT.match(override)
            if not match:
                return None, [
                    {
                        "line": args["override"]["line"],
                        "text": f'Override "{override}" is not a valid score or '
                        "modifier.",
                    }
                ]

            groups = match.groupdict()

            if groups["constraint"] and groups["constraint_value"]:
                constraint_int = int(groups["constraint_value"])
                if constraint_int < 1 or constraint_int > 30:
                    return None, [
                        {
                            "line": args["override"]["line"],
                            "text": (
                                f'Override "{groups["constraint"]} {constraint_int}" '
                                "is out of range (1-30)."
                            ),
                        }
                    ]

                args[groups["constraint"].lower()] = {
                    "value": groups["constraint_value"],
                    "line": args["override"]["line"],
                }
                if not groups["value"]:
                    args["override"]["value"] = groups["constraint_value"]

            if groups["value"]:
                if groups["modifier_sign"]:
                    args["override"]["value"] = (
                        groups["modifier_sign"] + groups["value"]
                    )
                else:
                    value_i = int(groups["value"])
                    if value_i < 1 or value_i > 30:
                        return None, [
                            {
                                "line": args["override"]["line"],
                                "text": f'Override "{value_i}" is out of range '
                                "(1-30).",
                            }
                        ]
                    args["override"]["value"] = groups["value"]

                if (
                    args["override"]["value"].startswith("+")
                    and not groups["constraint"]
                ):
                    args["maximum"] = {"value": "30", "line": args["override"]["line"]}
                elif (
                    args["override"]["value"].startswith("-")
                    and not groups["constraint"]
                ):
                    args["minimum"] = {"value": "1", "line": args["override"]["line"]}

        return cls.create_object(args, line), []

    def __str__(self) -> str:
        ability_name = self.ability.capitalize()

        string = f"{self.DIRECTIVE_NAME}: {ability_name} "

        if self.override:
            override_desc = self.override
            if self.minimum or self.maximum:
                if self.minimum:
                    override_desc = f"minimum {self.minimum}"
                if self.maximum:
                    override_desc = f"maximum {self.maximum}"
                if self.override.startswith(("+", "-")):
                    override_desc = f"{self.override}, {override_desc}"
            string = string + f"{override_desc} (override)"
        else:
            string = string + self.value

        return string

    def filter_fields(self) -> list:
        """Filter out maximum field if it's the default value of '20'."""
        if self.maximum == "20":
            return ["maximum"]
        return []

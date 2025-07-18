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
        index: int,
        args: dict,
    ) -> tuple[Optional["Set"], list]:

        index += 1  # 0-indexed

        errors = []

        # required arguments
        if "key" not in args:
            errors.append(
                {
                    "line": index,
                    "text": 'Required "key" argument is missing.',
                }
            )

        if "value" not in args:
            errors.append(
                {
                    "line": index,
                    "text": 'Required "value" argument is missing.',
                }
            )

        if errors:
            return None, errors

        # validate key
        key_value = args["key"]["value"]
        if not key_value.strip():
            return None, [
                {
                    "line": args["key"]["line"],
                    "text": f'Key "{key_value}" is not valid.',
                }
            ]

        # validate value
        value_value = args["value"]["value"]
        if not value_value.strip():
            return None, [
                {
                    "line": args["value"]["line"],
                    "text": f'Value "{value_value}" is not valid.',
                }
            ]

        return cls.create_object(args, index), []

    def __str__(self) -> str:
        return f"{self.DIRECTIVE_NAME}: {self.key} = '{self.value}'"

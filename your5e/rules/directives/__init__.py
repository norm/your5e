import importlib
import inspect
import pkgutil
from dataclasses import asdict as dc_asdict
from dataclasses import dataclass
from typing import Optional


@dataclass
class Directive:
    id: str = ""
    name: Optional[str] = None
    comment: Optional[str] = None

    @classmethod
    def generate_id(cls, line_number: int) -> str:
        class_name = cls.__name__.lower()
        return f"{class_name}_{line_number}"

    @classmethod
    def create_object(cls, args_data: dict, line_number: int):
        import inspect

        universal_keys = {"id", "name", "comment"}
        universal_args = {}
        directive_args = {}

        for key, arg in args_data.items():
            value = arg["value"]
            if key in universal_keys:
                universal_args[key] = value
            else:
                directive_args[key] = value

        if "id" not in universal_args:
            universal_args["id"] = cls.generate_id(line_number)

        sig = inspect.signature(cls.__init__)
        kwargs = {}

        for param_name in sig.parameters:
            if param_name == "self":
                continue
            elif param_name in universal_args:
                kwargs[param_name] = universal_args[param_name]
            else:
                kwargs[param_name] = directive_args.get(param_name)

        return cls(**kwargs)

    def asdict(self) -> dict:
        data = dc_asdict(self)
        return self._transform_dict(data)

    def _transform_dict(self, data: dict) -> dict:
        return data

    def __str__(self) -> str:
        return f"{self.DIRECTIVE_KEY} ..."

    def to_markdown(self) -> str:
        """Convert directive object back to Markdown format."""
        # Get directive-specific fields (excluding universal ones)
        universal_keys = {"id", "name", "comment"}
        data = self.asdict()
        directive_fields = {k: v for k, v in data.items() if k not in universal_keys}

        # Check if we can use shorthand format
        shorthand_key = getattr(self.__class__, "SHORTHAND_KEY", "key")
        shorthand_value = getattr(self.__class__, "SHORTHAND_VALUE", "value")

        # Check all fields (both directive-specific and universal)
        all_fields = data.copy()

        # Check if shorthand key exists in any field
        if shorthand_key not in all_fields:
            can_use_shorthand = False
        else:
            # For shorthand, need exactly shorthand fields, no others
            # Universal fields for shorthand: name (if shorthand key)
            # Universal fields preventing shorthand: comment, name (if not key)

            # Check if we have universal fields that would prevent shorthand
            # Universal fields for shorthand: name (if shorthand key/value)
            # Universal fields preventing: comment, other non-shorthand
            universal_shorthand_fields = (
                {shorthand_key, shorthand_value}
                if shorthand_key == "name" or shorthand_value == "name"
                else []
            )

            # Comment always prevents shorthand
            if self.comment:
                can_use_shorthand = False
            # If name is not part of shorthand, it prevents shorthand
            elif self.name and "name" not in universal_shorthand_fields:
                can_use_shorthand = False
            else:
                can_use_shorthand = True

            if can_use_shorthand:
                # Check directive fields, filter ignored for shorthand
                fields_to_filter = self.filter_fields()
                relevant_directive_fields = {
                    k: v
                    for k, v in directive_fields.items()
                    if v is not None and v != "" and k not in fields_to_filter
                }

                # For shorthand, determine which directive fields should be present
                expected_directive_fields = []

                # If shorthand key is in directive fields, it should be present
                if (
                    shorthand_key in directive_fields
                    and directive_fields[shorthand_key]
                ):
                    expected_directive_fields.append(shorthand_key)

                # If shorthand value is in directive fields, it should also be present
                if (
                    shorthand_value in directive_fields
                    and directive_fields[shorthand_value]
                ):
                    expected_directive_fields.append(shorthand_value)

                can_use_shorthand = sorted(relevant_directive_fields.keys()) == sorted(
                    expected_directive_fields
                )

        if can_use_shorthand:
            # Generate shorthand markdown format
            # Get key value from appropriate field (directive-specific or universal)
            if shorthand_key in all_fields:
                key_value = all_fields[shorthand_key]
            else:
                key_value = ""

            # Get value from appropriate field (directive-specific or universal)
            if shorthand_value in all_fields:
                value_value = all_fields[shorthand_value]
            else:
                value_value = directive_fields.get(shorthand_value, "")

            # Check for field-specific text conversion methods
            key_text_method = getattr(self, f"{shorthand_key}_as_text", None)
            if key_text_method and callable(key_text_method):
                key_value = key_text_method()

            value_text_method = getattr(self, f"{shorthand_value}_as_text", None)
            if value_text_method and callable(value_text_method):
                value_value = value_text_method()

            if value_value:
                return f"- {self.DIRECTIVE_NAME} _{key_value}_ {value_value}\n"
            else:
                return f"- {self.DIRECTIVE_NAME} _{key_value}_\n"

        # Use full format
        lines = [f"- {self.DIRECTIVE_NAME}"]

        # Add directive-specific fields first
        for key, value in directive_fields.items():
            if value is not None and value != "":
                # Check for field-specific text conversion method
                text_method = getattr(self, f"{key}_as_text", None)
                if text_method and callable(text_method):
                    value = text_method()
                lines.append(f"  - _{key}_ {value}")

        # Add universal fields if they exist
        if self.name:
            lines.append(f"  - _name_ {self.name}")
        if self.comment:
            lines.append(f"  - _comment_ {self.comment}")

        return "\n".join(lines) + "\n"

    def filter_fields(self) -> list:
        """Override in subclasses to return field names filtered for shorthand."""
        return []


# discover directive modules dynamically
_available_classes = []
DIRECTIVES = {}
for importer, modname, ispkg in pkgutil.iter_modules(__path__, __name__ + "."):
    if not ispkg:
        try:
            module = importlib.import_module(modname)
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and hasattr(obj, "DIRECTIVE_NAME")
                    and hasattr(obj, "DIRECTIVE_KEY")
                    and obj != Directive
                ):
                    globals()[name] = obj
                    _available_classes.append(name)
                    DIRECTIVES[obj.DIRECTIVE_NAME.lower()] = {
                        "class": obj,
                        "key": obj.DIRECTIVE_KEY,
                    }
        except ImportError:
            pass


__all__ = [
    "Directive",
    "DirectiveParseError",
    "DIRECTIVES",
] + _available_classes

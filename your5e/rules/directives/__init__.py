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

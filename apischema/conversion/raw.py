from dataclasses import MISSING, field, make_dataclass
from inspect import Parameter, signature
from typing import Any, Callable, List, Mapping, TypeVar

from apischema.conversion.converters import deserializer
from apischema.conversion.utils import Conversions, Converter
from apischema.fields import with_fields_set
from apischema.typing import get_type_hints
from apischema.utils import MakeDataclassField, as_dict, to_camel_case


def to_raw_deserializer(func: Callable) -> Converter:
    types = get_type_hints(func, include_extras=True)
    if "return" not in types:
        raise TypeError("Return must be annotated")
    sig = signature(func)
    fields: List[MakeDataclassField] = []
    kwargs = None
    for name, param in sig.parameters.items():
        if param.kind == Parameter.POSITIONAL_ONLY:  # pragma: no cover
            raise TypeError("Forbidden positional-only parameter")
        if param.kind == Parameter.VAR_POSITIONAL:
            raise TypeError("Forbidden variadic positional parameter")
        if param.kind == Parameter.VAR_KEYWORD:
            from apischema import properties

            field_ = field(default_factory=dict, metadata=properties)
            type_ = Mapping[str, types.get(name, Any)]  # type: ignore
            fields.append((name, type_, field_))  # type: ignore
            kwargs = name
            continue
        default = param.default if param.default is not Parameter.empty else MISSING
        try:
            fields.append((name, types[name], field(default=default)))
        except KeyError:
            raise TypeError("All parameters must be annotated")

    def converter(obj):
        kw = as_dict(obj)
        kw.update(kw.pop(kwargs, ()))
        return func(**kw)

    cls = with_fields_set(make_dataclass(to_camel_case(func.__name__), fields))
    converter.__annotations__ = {"obj": cls, "return": types["return"]}
    return converter


Func = TypeVar("Func", bound=Callable)


def raw_deserializer(func: Func, conversions: Conversions = None) -> Func:
    deserializer(to_raw_deserializer(func), conversions=conversions)
    return func

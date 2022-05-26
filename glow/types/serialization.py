"""
This module contains the public API for artifact serialization.
"""
# Standard library
import abc
import base64
import dataclasses
import typing
import inspect
import json

# Third-party
import cloudpickle  # type: ignore

# Glow
from glow.types.generic_type import GenericType
from glow.types.registry import (
    DataclassKey,
    get_to_json_encodable_func,
    get_from_json_encodable_func,
    is_glow_parametrized_generic_type,
    is_valid_typing_alias,
    get_origin_type,
)


# VALUE SERIALIZATION


# type_ must be `typing.Any` because `typing` aliases are not type
def value_to_json_encodable(value: typing.Any, type_: typing.Any) -> typing.Any:
    # First we check if there is a registered serializer for this exact type
    to_json_encodable_func = get_to_json_encodable_func(type_)

    # If not we check if this is a dataclass
    if to_json_encodable_func is None and dataclasses.is_dataclass(type_):
        to_json_encodable_func = get_to_json_encodable_func(DataclassKey)

    # If we have a serializer, we use it
    if to_json_encodable_func is not None:
        return to_json_encodable_func(value, type_)

    # Otherwise we default
    try:
        # We try to dump to JSON, this is innefficient, how else can we test this?
        json.dumps(value)
        return value
    except Exception:
        # Otherwise we pickle by default
        return binary_to_string(cloudpickle.dumps(value))


def value_from_json_encodable(
    json_encodable: typing.Any, type_: typing.Any
) -> typing.Any:
    """
    Public API to deserialize a JSON-encodable payload into its
    corresponding value using the deserialization of `type_`.
    """
    # First we check whether this is a deserializer for type_.
    from_json_encodable_func = get_from_json_encodable_func(type_)

    # Then we check if this is a dataclass
    if from_json_encodable_func is None and dataclasses.is_dataclass(type_):
        from_json_encodable_func = get_from_json_encodable_func(DataclassKey)

    # If we have a deserializer we use it
    if from_json_encodable_func is not None:
        return from_json_encodable_func(json_encodable, type)

    # Otherwise we default
    try:
        # Is this a pickle payload?
        return cloudpickle.loads(binary_from_string(json_encodable))
    except Exception:
        # If not the raw value must have already been
        # JSON encodable
        return json_encodable


def binary_to_string(binary: bytes) -> str:
    return base64.b64encode(binary).decode("ascii")


def binary_from_string(string: str) -> bytes:
    return base64.b64decode(string.encode("ascii"))


# JSON SUMMARIES
def get_json_encodable_summary(value: typing.Any, type_: typing.Any) -> typing.Any:
    # First we check custom summaries
    # TODO

    # By default we use the full payload
    return value_to_json_encodable(value, type_)


# TYPE SERIALIZATION


def type_to_json_encodable(type_: typing.Any) -> typing.Dict[str, typing.Any]:

    registry: typing.Dict[str, typing.Any] = dict()

    _populate_registry(type_, registry)

    return {
        "type": _type_repr(type_),
        "registry": registry,
    }


def _type_repr(
    type_: typing.Any,
) -> typing.Tuple[str, str, typing.Dict[str, typing.Any]]:
    return (_get_category(type_), _get_key(type_), _get_parameters(type_))


_BUILTINS = (float, int, str, bool, type(None), bytes)


def _is_builtin(type_: typing.Any) -> bool:
    """
    Is this type a Python native builtin type?
    """
    return type_ in _BUILTINS


def _is_dataclass(type_: typing.Any) -> bool:
    # We don't use dataclasses.is_dataclass because we don't
    # want to know whether any parent classes are dataclasses, just
    # this one
    return "__dataclass_fields__" in type_.__dict__


def _get_category(type_: typing.Any) -> str:
    if _is_builtin(type_):
        return "builtin"

    if _is_dataclass(type_):
        return "dataclass"

    if is_valid_typing_alias(type_):
        return "typing"

    if is_glow_parametrized_generic_type(type_):
        return "generic"

    # Just a plain old class
    return "class"


_SPECIAL_FORM_MAPPING = {
    typing.Union: "Union",
}


def _get_key(type_: typing.Any) -> str:
    """
    Get a unique str key for a given type.

    For most types (builtins, classes, etc) the key is simply
    the name of the type (`int`, `float`, `NoneType`, `str`, `bool`, etc.).

    For subscripted generics, it is the name of the __origin__ type. For example:
     `typing.List[int]` -> `list`, `Union[int, float]` -> `Union`, etc.
    """
    # We want the unsubscripted or parametrized generic
    origin_type = get_origin_type(type_)

    try:
        # Most have a __name__ attribute
        return origin_type.__name__
    except AttributeError:
        pass

    # instances of `typing._SpecialForm` don't have __name__
    if origin_type in _SPECIAL_FORM_MAPPING:
        return _SPECIAL_FORM_MAPPING[origin_type]

    raise Exception("Unable to get type key for: {}".format(type_))


def _get_parameters(type_: typing.Any) -> typing.Dict[str, typing.Any]:
    if _is_builtin(type_):
        return {}

    if is_valid_typing_alias(type_):
        return {"args": [_parameter_repr(arg) for arg in type_.__args__]}

    if _is_dataclass(type_):
        return {
            "import_path": type_.__module__,
            "fields": {
                name: _parameter_repr(field.type)
                for name, field in type_.__dataclass_fields__.items()
            },
        }

    if is_glow_parametrized_generic_type(type_):
        return {
            # This has to be a list so we maintain the order when sort_key=True
            # on json.dumps
            # This is necessary because [] does nto accept keyword arguments
            # so we have to pass them in the right order.
            "parameters": [
                (key, _parameter_repr(param))
                for key, param in type_.get_parameters().items()
            ]
        }

    return {"import_path": type_.__module__}


def _parameter_repr(value: typing.Any) -> typing.Any:
    def _is_type(type_) -> bool:
        return isinstance(type_, type) or is_valid_typing_alias(value)

    if _is_type(value):
        return {"type": _type_repr(value)}

    def _is_scalar(v):
        # is not a type or a class or a function or a sequence or a mapping
        return (
            (isinstance(v, str) or not isinstance(v, (typing.Sequence, typing.Mapping)))
            and not _is_type(v)
            and not inspect.isclass(v)
            and not inspect.isfunction(v)
        )

    if isinstance(value, typing.Sequence):
        if any(not _is_scalar(item) for item in value):
            return list(map(_parameter_repr, value))

    if isinstance(value, typing.Mapping):
        if any(not _is_scalar(item) for item in value.values()):
            return {k: _parameter_repr(v) for k, v in value.items()}

    return {"value": value}


def _populate_registry(
    type_: typing.Any, registry: typing.Dict[str, typing.Any]
) -> None:
    def _include_in_registry(t) -> bool:
        return t not in (object, abc.ABC, GenericType)

    if not _include_in_registry(type_):
        return

    if is_glow_parametrized_generic_type(type_):
        _populate_registry_from_parameters(type_.get_parameters(), registry)

    if is_valid_typing_alias(type_):
        _populate_registry_from_parameters(type_.__args__, registry)

    if _is_dataclass(type_):
        _populate_registry_from_parameters(
            {name: field.type for name, field in type_.__dataclass_fields__.items()},
            registry,
        )

    type_key = _get_key(type_)

    registry[type_key] = []

    bases: typing.Tuple[type, ...] = tuple()
    try:
        bases = type_.__bases__
    except AttributeError:
        pass

    for parent_type in bases:
        if not _include_in_registry(parent_type):
            continue

        _populate_registry(parent_type, registry)

        # A non-parametrized generic
        if issubclass(
            parent_type, GenericType
        ) and not is_glow_parametrized_generic_type(parent_type):
            continue

        registry[type_key].append(_type_repr(parent_type))


def _populate_registry_from_parameters(parameters, registry):
    if isinstance(parameters, type) or is_valid_typing_alias(parameters):
        _populate_registry(parameters, registry)

    if isinstance(parameters, _BUILTINS):
        return

    if isinstance(parameters, typing.Sequence):
        for parameter in parameters:
            _populate_registry_from_parameters(parameter, registry)

    if isinstance(parameters, typing.Mapping):
        for parameter in parameters.values():
            _populate_registry_from_parameters(parameter, registry)

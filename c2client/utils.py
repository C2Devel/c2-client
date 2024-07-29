import os
from typing import Any

from botocore.model import ListShape, StructureShape, Shape

from c2client.errors import EnvironmentVariableError, MalformedParametersError


def from_dot_notation(source):
    """Converts a incoming query to a request dictionary.
    For example::
        1. {"Action": ["Action"], "Param": ["Value"]}
        2. {"Action": ["Action"], "Param.2": ["Value2"], "Param.1": ["Value1"]}
        3. {"Action": ["Action"], "Param.SubParam": ["Value"]}
    would  result in the params dict::
        1. {"Action": "Action", "Param": "Value"}
        2. {"Action": "Action", "Param": ["Value1", "Value2"]}
        3. {"Action": "Action", "Param": { "SubParam": "Value"}}
    :type query: dict
    :param query: This is dictionary, returned by '_get_query()'.
    """
    result = {"result": {}}
    for key, value in sorted(source.items()):
        try:
            _process_tokens(key.split("."), value, result, "result")
        except Exception:
            raise MalformedParametersError
    return result["result"]


def _process_tokens(tokens, value, parent, index):
    key, rest = tokens[0], tokens[1:]
    if key.isdigit():
        key = int(key) - 1

    if not isinstance(key, int):
        parent[index].setdefault(key, {})
    elif isinstance(parent[index], dict) and not parent[index]:
        parent[index] = [{}]
    elif isinstance(parent[index], list) and len(parent[index]) == key:
        parent[index].append({})
    elif not (isinstance(parent[index], list) and len(parent[index]) > key):
        raise MalformedParametersError

    if rest:
        _process_tokens(rest, value, parent[index], key)
    else:
        parent[index][key] = value


def get_env_var(name):
    """Returns env_var by it's name or raises EnvironmentError."""

    env_var = os.environ.get(name)
    if env_var is None:
        raise EnvironmentVariableError(name)
    return env_var


def convert_args(params: Any, shape: Shape):
    """Converts values in the params dictionary to the types expected by shape."""

    if not isinstance(shape, StructureShape):
        return convert_arg(value=params, shape=shape)

    converted_params = {}

    for param_name, param_value in params.items():
        if param_name in shape.members:
            member_shape = shape.members[param_name]
            converted_params[param_name] = convert_arg(param_value, member_shape)
        else:
            converted_params[param_name] = param_value

    return converted_params


def convert_arg(value: Any, shape: Shape):
    """Converts an individual value to the type expected by shape."""

    if isinstance(shape, ListShape):
        if not isinstance(value, list):
            raise ValueError(f"Expected list for {shape.name}, got {type(value).__name__}")
        return [convert_arg(v, shape.member) for v in value]

    elif isinstance(shape, StructureShape):
        if not isinstance(value, dict):
            raise ValueError(f"Expected dict for {shape.name}, got {type(value).__name__}")
        return convert_args(value, shape)

    elif shape.type_name == 'string':
        return str(value)

    elif shape.type_name == 'integer' or shape.type_name == "long":
        return int(value)

    elif shape.type_name == 'float' or shape.type_name == "double":
        return float(value)

    elif shape.type_name == 'boolean':
        if isinstance(value, str) and value.lower() == 'false':
            return False
        return bool(value)
    else:
        return value

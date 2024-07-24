import os

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

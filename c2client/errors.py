"""c2client errors."""


class EnvironmentVariableError(Exception):
    def __init__(self, name):
        super(EnvironmentVariableError, self).__init__(
            "Environment variable '{0}' not found.".format(name.upper()))


class MalformedParametersError(Exception):
    def __init__(self):
        super(MalformedParametersError, self).__init__("Malformed parameters.")

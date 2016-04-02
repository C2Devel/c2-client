from distutils.version import StrictVersion
from types import MethodType
from six.moves.urllib.parse import urlparse

import boto.ec2
import boto.ec2.cloudwatch

from boto.ec2.regioninfo import RegionInfo


BOTO_COMPAT_VERSION = StrictVersion("2.12.0")
"""Boto compat version for CROC Cloud Platform."""

CONNECTIONS_MAP = {
    "cw": boto.ec2.cloudwatch.CloudWatchConnection,
    "ec2": boto.ec2.EC2Connection,
}
"""Connection classes map."""


def __patch_auth_capability(connection):
    """Patches connection class for using old auth method."""

    if StrictVersion(boto.__version__) > BOTO_COMPAT_VERSION:
        _required_auth_capability = MethodType(
            lambda self: ["ec2"], connection)
        setattr(connection,
            "_required_auth_capability", _required_auth_capability)

    return connection


def get_connection(service, endpoint, **kwargs):
    """Returns connection to specified Cloud service."""

    parsed = urlparse(endpoint)
    kwargs["port"] = parsed.port
    kwargs["path"] = parsed.path

    kwargs["region"] = RegionInfo(
        name=parsed.hostname, endpoint=parsed.hostname)

    klass = __patch_auth_capability(CONNECTIONS_MAP[service])

    return klass(**kwargs)

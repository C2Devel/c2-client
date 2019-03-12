from six.moves.urllib.parse import urlparse

import boto.cloudtrail.layer1
import boto.ec2
import boto.ec2.cloudwatch

from boto.ec2.regioninfo import RegionInfo


CONNECTIONS_MAP = {
    "ct": boto.cloudtrail.layer1.CloudTrailConnection,
    "cw": boto.ec2.cloudwatch.CloudWatchConnection,
    "ec2": boto.ec2.EC2Connection,
}
"""Connection classes map."""


def get_connection(service, endpoint, **kwargs):
    """Returns connection to specified Cloud service."""

    parsed = urlparse(endpoint)
    kwargs["port"] = parsed.port
    kwargs["path"] = parsed.path

    kwargs["region"] = RegionInfo(
        name=parsed.hostname, endpoint=parsed.hostname)

    klass = CONNECTIONS_MAP[service]

    return klass(**kwargs)

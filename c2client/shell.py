from __future__ import print_function, unicode_literals

import argparse
import codecs
import json
import os
import ssl
import sys

import boto

from functools import wraps

from c2client.compat import get_connection
from c2client.utils import prettify_xml, from_dot_notation

# Nasty hack to workaround default ascii codec
if sys.version_info[0] < 3:
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf8')(sys.stderr)

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

if os.environ.get("DEBUG"):
    boto.set_stream_logger("c2")


class EnvironmentVariableError(Exception):
    def __init__(self, name):
        super(EnvironmentVariableError, self).__init__(
            "Environment variable '{0}' not found.".format(name.upper()))


def configure_boto():
    """Configure boto runtime for CROC Cloud"""

    if not boto.config.has_section("Boto"):
        boto.config.add_section("Boto")
    boto.config.set("Boto", "is_secure", "True")
    boto.config.set("Boto", "num_retries", "0")
    boto.config.set("Boto", "https_validate_certificates", "False")


def exitcode(func):
    """Wrapper for logging any catched exception."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            return e
    return wrapper


def parse_arguments(program):
    """
    Parse incoming action and arguments as a dictionary
    for support AWS API requests format.
    """

    parser = argparse.ArgumentParser(prog=program)
    parser.add_argument("action", help="The action that you want to perform.")
    parser.add_argument("parameters", nargs="*",
        help="Any parameters for the action. "
             "Parameters specified by parameter key and "
             "parameter value separated by space.")
    args = parser.parse_args()

    params = args.parameters
    parameters = dict(zip(params[::2], params[1::2]))

    return args.action, parameters


@exitcode
def ec2_main():
    """Main function for EC2 API Client."""

    action, args = parse_arguments("c2-ec2")

    configure_boto()
    ec2_endpoint = os.environ.get("EC2_URL")
    if not ec2_endpoint:
        raise EnvironmentVariableError("EC2_URL")

    connection = get_connection("ec2", ec2_endpoint)
    response = connection.make_request(action, args)

    print(prettify_xml(response.read()))


@exitcode
def cw_main():
    """Main function for CloudWatch API Client."""

    action, args = parse_arguments("c2-cw")

    configure_boto()
    cloudwatch_endpoint = os.environ.get("AWS_CLOUDWATCH_URL")
    if not cloudwatch_endpoint:
        raise EnvironmentVariableError("AWS_CLOUDWATCH_URL")

    connection = get_connection("cw", cloudwatch_endpoint)
    response = connection.make_request(action, args)

    print(prettify_xml(response.read()))


@exitcode
def ct_main():
    """Main function for CloudTrail API Client."""

    action, args = parse_arguments("c2-ct")

    configure_boto()
    cloudtrail_endpoint = os.environ.get("AWS_CLOUDTRAIL_URL")
    if not cloudtrail_endpoint:
        raise EnvironmentVariableError("AWS_CLOUDTRAIL_URL")

    connection = get_connection("ct", cloudtrail_endpoint)
    if "MaxResults" in args:
        args["MaxResults"] = int(args["MaxResults"])
    if "StartTime" in args:
        args["StartTime"] = int(args["StartTime"])
    if "EndTime" in args:
        args["EndTime"] = int(args["EndTime"])

    response = connection.make_request(action, json.dumps(from_dot_notation(args)))

    print(json.dumps(response, indent=4, sort_keys=True))

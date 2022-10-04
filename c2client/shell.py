from __future__ import print_function, unicode_literals

import argparse
import codecs
import json
import os
import ssl
import sys

import boto
import boto3
import inflection

from functools import wraps

from c2client.compat import get_connection
from c2client.utils import prettify_xml, from_dot_notation, get_env_var

# Nasty hack to workaround default ascii codec
if sys.version_info[0] < 3:
    sys.stdout = codecs.getwriter("utf8")(sys.stdout)
    sys.stderr = codecs.getwriter("utf8")(sys.stderr)

if hasattr(ssl, "_create_unverified_context"):
    ssl._create_default_https_context = ssl._create_unverified_context

if os.environ.get("DEBUG"):
    boto.set_stream_logger("c2")


def get_boto3_client(service, endpoint, aws_access_key_id, aws_secret_access_key, verify):
    """Returns boto3 client connection to specified Cloud service."""

    return boto3.client(
        service,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name="croc",
        endpoint_url=endpoint,
        verify=verify,
    )


def configure_boto(verify):
    """Configure boto runtime for CROC Cloud"""

    if not boto.config.has_section("Boto"):
        boto.config.add_section("Boto")
    boto.config.set("Boto", "is_secure", "True")
    boto.config.set("Boto", "num_retries", "0")
    boto.config.set("Boto", "https_validate_certificates", str(verify))


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
    parser.add_argument(
        "--no-verify-ssl",
        action="store_false",
        help="disable verifying ssl certificate",
        required=False)
    parser.add_argument("parameters", nargs="*",
        help="Any parameters for the action. "
             "Parameters specified by parameter key and "
             "parameter value separated by space.")
    args = parser.parse_args()

    params = args.parameters
    no_verify_ssl = args.no_verify_ssl
    parameters = dict(zip(params[::2], params[1::2]))

    return args.action, parameters, no_verify_ssl


@exitcode
def ec2_main():
    """Main function for EC2 API Client."""

    action, args, verify = parse_arguments("c2-ec2")

    configure_boto(verify)
    ec2_endpoint = get_env_var("EC2_URL")

    connection = get_connection("ec2", ec2_endpoint)
    response = connection.make_request(action, args)

    print(prettify_xml(response.read()))


@exitcode
def cw_main():
    """Main function for CloudWatch API Client."""

    action, args, verify = parse_arguments("c2-cw")

    configure_boto(verify)
    cloudwatch_endpoint = get_env_var("AWS_CLOUDWATCH_URL")

    connection = get_connection("cw", cloudwatch_endpoint)
    response = connection.make_request(action, args)

    print(prettify_xml(response.read()))


@exitcode
def ct_main():
    """Main function for CloudTrail API Client."""

    action, args, verify = parse_arguments("c2-ct")

    configure_boto(verify)
    cloudtrail_endpoint = get_env_var("AWS_CLOUDTRAIL_URL")

    connection = get_connection("ct", cloudtrail_endpoint)
    if "MaxResults" in args:
        args["MaxResults"] = int(args["MaxResults"])
    if "StartTime" in args:
        args["StartTime"] = int(args["StartTime"])
    if "EndTime" in args:
        args["EndTime"] = int(args["EndTime"])

    response = connection.make_request(action, json.dumps(from_dot_notation(args)))

    print(json.dumps(response, indent=4, sort_keys=True))


@exitcode
def eks_main():
    """Main function for EKS API Client."""

    action, args, verify = parse_arguments("c2-eks")

    for key, value in args.items():
        if value.isdigit():
            args[key] = int(value)
        elif value.lower() == "true":
            args[key] = True
        elif value.lower() == "false":
            args[key] = False

    eks_endpoint = get_env_var("EKS_URL")

    aws_access_key_id = get_env_var("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_env_var("AWS_SECRET_ACCESS_KEY")

    eks_client = get_boto3_client("eks", eks_endpoint, aws_access_key_id, aws_secret_access_key, verify)

    result = getattr(eks_client, inflection.underscore(action))(**from_dot_notation(args))

    result.pop("ResponseMetadata", None)

    print(json.dumps(result, indent=4, sort_keys=True))

@exitcode
def paas_main():
    """Main function for PaaS API Client."""

    action, args, verify = parse_arguments("c2-paas")

    for key, value in args.items():
        if value.isdigit():
            args[key] = int(value)
        elif value.lower() == "true":
            args[key] = True
        elif value.lower() == "false":
            args[key] = False

    paas_endpoint = get_env_var("PAAS_URL")

    aws_access_key_id = get_env_var("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_env_var("AWS_SECRET_ACCESS_KEY")

    paas_client = get_boto3_client("paas", paas_endpoint, aws_access_key_id, aws_secret_access_key, verify)

    result = getattr(paas_client, inflection.underscore(action))(**from_dot_notation(args))

    result.pop("ResponseMetadata", None)

    print(json.dumps(result, indent=4, sort_keys=True))


@exitcode
def autoscaling_main():
    """Main function for Auto Scaling API Client."""

    action, args, verify = parse_arguments("c2-as")

    for key, value in args.items():
        if value.isdigit():
            args[key] = int(value)
        elif value.lower() == "true":
            args[key] = True
        elif value.lower() == "false":
            args[key] = False

    auto_scaling_endpoint = get_env_var("AUTO_SCALING_URL")

    aws_access_key_id = get_env_var("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_env_var("AWS_SECRET_ACCESS_KEY")

    auto_scaling_client = get_boto3_client("autoscaling", auto_scaling_endpoint, aws_access_key_id,
                                           aws_secret_access_key, verify)

    result = getattr(auto_scaling_client, inflection.underscore(action))(**from_dot_notation(args))

    result.pop("ResponseMetadata", None)

    print(json.dumps(result, indent=4, sort_keys=True))

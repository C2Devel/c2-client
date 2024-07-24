import argparse
import json
import re
import ssl
from abc import abstractmethod
from functools import wraps
from typing import Dict

import boto3
import inflection

from c2client.utils import from_dot_notation, get_env_var


ssl._create_default_https_context = ssl._create_unverified_context


def exitcode(func: callable):
    """Wrapper for logging any caught exception."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            return e
    return wrapper


def parse_arguments():
    """
    Parse incoming action and arguments as a dictionary
    for support AWS API requests format.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="The action that you want to perform.")
    parser.add_argument(
        "--no-verify-ssl",
        action="store_false",
        help="disable verifying ssl certificate",
        required=False
    )
    parser.add_argument(
        "parameters",
        nargs="*",
        help="Any parameters for the action. "
             "Parameters specified by parameter key and "
             "parameter value separated by space."
    )
    args = parser.parse_args()

    params = args.parameters
    no_verify_ssl = args.no_verify_ssl
    parameters = dict(zip(params[::2], params[1::2]))

    return args.action, parameters, no_verify_ssl


class BaseClient:

    url_key: str
    client_name: str
    use_base_access_key: bool = False

    @classmethod
    @abstractmethod
    def make_request(cls, method: str, arguments: Dict[str, str], verify: bool):
        """Run request."""

        raise NotImplementedError

    @classmethod
    @exitcode
    def execute(cls):
        """Main function for API client."""

        action, arguments, verify = parse_arguments()
        response = cls.make_request(action, arguments, verify)

        print(response)


class C2Client(BaseClient):

    @classmethod
    def get_client(cls, verify: bool):
        """Return boto3 client."""

        endpoint = get_env_var(cls.url_key)

        aws_access_key_id = get_env_var("AWS_ACCESS_KEY_ID")
        base_access_key = get_env_var("BASE_ACCESS_KEY")
        aws_secret_access_key = get_env_var("AWS_SECRET_ACCESS_KEY")

        return boto3.client(
            cls.client_name,
            aws_access_key_id=base_access_key if cls.use_base_access_key else aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name="croc",
            endpoint_url=endpoint,
            verify=verify,
        )

    @classmethod
    def is_conversion_needed(cls, argument_name: str) -> bool:
        """Check whether type conversion is needed for argument."""

        return True

    @classmethod
    def make_request(cls, method: str, arguments: dict, verify: bool):

        client = cls.get_client(verify)

        for key, value in arguments.items():
            if not cls.is_conversion_needed(key):
                continue
            if value.isdigit():
                arguments[key] = int(value)
            elif value.lower() == "true":
                arguments[key] = True
            elif value.lower() == "false":
                arguments[key] = False

        result = getattr(client, inflection.underscore(method))(**from_dot_notation(arguments))

        result.pop("ResponseMetadata", None)

        # default=str is required for serializing Datetime objects
        return json.dumps(result, indent=4, default=str)


class EC2Client(C2Client):

    url_key = "EC2_URL"
    client_name = "ec2"


class CWClient(C2Client):

    url_key = "AWS_CLOUDWATCH_URL"
    client_name = "cloudwatch"


class CTClient(C2Client):

    url_key = "AWS_CLOUDTRAIL_URL"
    client_name = "cloudtrail"

    @classmethod
    def make_request(cls, method: str, arguments: dict, verify: bool):

        client = cls.get_client(verify)

        if "MaxResults" in arguments:
            arguments["MaxResults"] = int(arguments["MaxResults"])
        if "StartTime" in arguments:
            arguments["StartTime"] = int(arguments["StartTime"])
        if "EndTime" in arguments:
            arguments["EndTime"] = int(arguments["EndTime"])

        result = getattr(client, inflection.underscore(method))(**from_dot_notation(arguments))

        result.pop("ResponseMetadata", None)

        return json.dumps(result, indent=4, sort_keys=True)


class ASClient(C2Client):

    url_key = "AUTO_SCALING_URL"
    client_name = "autoscaling"

    @classmethod
    def is_conversion_needed(cls, argument_name: str) -> bool:
        """Check whether type conversion is needed for argument."""

        patterns = (
            r"Filters\.\d+\.Values\.\d+",
        )
        for pattern in patterns:
            if re.fullmatch(pattern, argument_name):
                return False
        return True


class BSClient(C2Client):

    url_key = "BACKUP_URL"
    client_name = "backup"


class EKSClient(C2Client):

    url_key = "EKS_URL"
    client_name = "eks"


class LegacyEKSClient(C2Client):

    url_key = "LEGACY_EKS_URL"
    client_name = "eks-legacy"


class PaasClient(C2Client):

    url_key = "PAAS_URL"
    client_name = "paas"


class ELBClient(C2Client):

    url_key = "ELB_URL"
    client_name = "elbv2"


class Route53Client(C2Client):

    url_key = "ROUTE53_URL"
    client_name = "route53"


class EFSClient(C2Client):

    url_key = "EFS_URL"
    client_name = "efs"


class IAMClient(C2Client):

    url_key = "IAM_URL"
    client_name = "iam"
    use_base_access_key = True


class DirectConnectClient(C2Client):

    url_key = "DIRECT_CONNECT_URL"
    client_name = "directconnect"

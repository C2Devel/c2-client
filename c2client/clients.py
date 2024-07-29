import argparse
import json
import ssl
from abc import abstractmethod
from functools import wraps
from typing import Dict

import boto3
import inflection

from c2client.utils import from_dot_notation, get_env_var, convert_args


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
    def make_request(cls, method: str, arguments: dict, verify: bool):

        client = cls.get_client(verify)

        if arguments:
            shape = client.meta.service_model.operation_model(method).input_shape
            arguments = convert_args(from_dot_notation(arguments), shape)

        result = getattr(client, inflection.underscore(method))(**arguments)

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


class ASClient(C2Client):

    url_key = "AUTO_SCALING_URL"
    client_name = "autoscaling"


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

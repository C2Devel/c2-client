from setuptools import setup, find_packages

import os

from c2client import __version__


PACKAGE_PATH = os.path.abspath(os.path.dirname(__file__))


def get_description():
    with open(os.path.join(PACKAGE_PATH, "README.rst")) as readme:
        return readme.read()


install_requires = [
    "boto",
    "boto3",
    "botocore",
    "inflection==0.3.1",
    "lxml",
]

entrypoints = [
    ("c2-as", "ASClient"),
    ("c2-bs", "BSClient"),
    ("c2-ct", "CTClient"),
    ("c2-cw", "CWClient"),
    ("c2-ec2", "EC2Client"),
    ("c2-efs", "EFSClient"),
    ("c2-eks", "EKSClient"),
    ("c2-eks-legacy", "LegacyEKSClient"),
    ("c2-elb", "ELBClient"),
    ("c2-iam", "IAMClient"),
    ("c2-paas", "PaasClient"),
    ("c2-route53", "Route53Client"),
    ("c2-dc", "DirectConnectClient"),
]

setup(
    name="c2client",
    version=__version__,
    description="CROC Cloud Platform - API Client",
    long_description=get_description(),
    url="https://github.com/c2devel/c2-client",
    license="GPL3",
    author="CROC Cloud Team",
    author_email="devel@croc.ru",
    maintainer="Andrey Kulaev",
    maintainer_email="adkulaev@gmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    install_requires=install_requires,
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            f"{name} = c2client.clients:{client}.execute"
            for name, client in entrypoints
        ] + [
            "c2rc-convert = c2client.c2rc_convert:main",
        ]
    },
)

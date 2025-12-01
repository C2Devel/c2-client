K2 Cloud API Client
=====================

Simple command-line utility for sending custom requests to K2 Cloud platform.

**Warning: this utility is not intended for automation cases.
Use https://github.com/c2devel/boto3.git and python scripts instead.**

Installation
------------

C2client package relies on forked versions of boto3 and botocore from the `C2Devel/boto3 <https://github.com/c2Devel/boto3>`_ and `C2Devel/botocore <https://github.com/c2Devel/botocore>`_ repositories. For isolated use our dependencies, it is highly recommended to use a virtual environment.


1. Clone the repository

    .. code-block:: bash 

       git clone https://github.com/C2Devel/c2-client.git && cd c2-client
       
2. Setup the virtual environment(Unix based system)

    .. code-block:: bash 

       python3 -m venv .venv && source .venv/bin/activate
       
3. Install the package in editable mode along with dependencies from requirements.txt

    .. code-block:: bash

       pip install -e . -r requirements.txt


Usage
-----

.. code-block::

   $ c2-ec2 --help
   usage: c2-ec2 [-h] action [parameters [parameters ...]]

   positional arguments:
      action          The action that you want to perform.
      parameters      Any parameters for the action. Parameters specified by parameter
                      key and parameter value separated by space.

   optional arguments:
      -h, --help      show this help message and exit
      --no-verify-ssl disable verifying ssl certificate


Common request syntax:

.. code-block:: bash

   $ c2-ec2 <action> <arg1> <value1> <arg2> <value2>


Example
-------

Send simple request:

.. code-block:: bash

   $ c2-ec2 RunInstances ImageId cmi-078880A0 Description "Test instance" \
   InstanceType m1.small MaxCount 1 MinCount 1 SecurityGroup.1 test

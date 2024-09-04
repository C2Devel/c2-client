CROC Cloud API Client
=====================

Simple command-line utility for sending custom requests to CROC Cloud platform.

**Warning: this utility is not intended for automation cases.
Use https://github.com/c2devel/boto3.git and python scripts instead.**

Installation
------------

Using pip:

   .. code-block:: bash

      $ pip install c2client

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

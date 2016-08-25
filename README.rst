ThingLoad - An AWS IoT Demonstrator
===================================

This is a sample project to push the CPU load of a windows machine to AWS IoT using python.

It shall demonstrate the use of the device shadow.

It uses the AWSIoTPythonSDK https://github.com/aws/aws-iot-device-sdk-python.

Features:

- Fetch CPU load from Windows (done)
- Publish the CPU load to an AWS IoT shadow (done)
- The publish rate is a Shadow Attribute and can be changed (proposed) by others (planned)

Installation
~~~~~~~~~~~~

Minimum Requirements
____________________

-  Python 3.5+
-  Windows 7+ (because it calls windows commands to fetch the cpu load)
-  OpenSSL version 1.0.1+ (TLS version 1.2) compiled with the Python executable for
   X.509 certificate-based mutual authentication

   To check your version of OpenSSL, use the following command in a Python interpreter:

   .. code-block:: python

       >>> import ssl
       >>> ssl.OPENSSL_VERSION

Usage
~~~~~

python -m thingload -r <rootCAFilePath> -c <certFilePath> -k <privateKeyFilePath>

Example:
python -m thingload -r "D:\VeriSign-Class 3-Public-Primary-Certification-Authority-G5.pem" -k "D:\1234567890-private.pem.key" -c "D:\1234567890-certificate.pem.crt" -t MyComputer

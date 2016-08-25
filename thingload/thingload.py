'''
/*
 * Copyright 2016 Alexander Schmitt
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

import getopt
import json
import logging
import re
import subprocess
import sys
import time

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

from . import config


# Usage
usageInfo = """Usage:
python -m thingload -r <rootCAFilePath> -c <certFilePath> -k <privateKeyFilePath>
Type "python -m thingload -h" for available options.
"""

# Help info
helpInfo = """-e, --endpoint
    Your AWS IoT custom endpoint
-r, --rootCA
    Root CA file path
-c, --cert
    Certificate file path
-k, --key
    Private key file path
-v, --verbose
    Print Debug logs
-h, --help
    Help information
"""


def customShadowCallback_Update(payload, responseStatus, token):
    # payload is a JSON string ready to be parsed using json.loads(...)
    # in both Py2.x and Py3.x
    if responseStatus == "timeout":
        print("Update request " + token + " time out!")
    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Update request with token: " + token + " accepted!")
        print("cpu load: " + str(payloadDict["state"]["reported"]["cpuload"]))
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")
    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")


def customShadowCallback_Delete(payload, responseStatus, token):
    if responseStatus == "timeout":
        print("Delete request " + token + " time out!")
    if responseStatus == "accepted":
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Delete request with token: " + token + " accepted!")
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")
    if responseStatus == "rejected":
        print("Delete request " + token + " rejected!")


def customShadowCallback_deltaCallback(payload, responseStatus, token):
    print("Delta Callback")


def fetchCpuLoad():
    wmic = subprocess.run(
        ["wmic", "cpu", "get", "loadpercentage"],
        stdout=subprocess.PIPE,
        universal_newlines=False)
    match = re.search("[0-9]+", wmic.stdout.decode("utf-8"))
    if match:
        return match.group(0)
    else:
        return "unknown"


def publishCpuLoad(shadow):
        JSONPayload = \
            '{"state":{"reported":{"cpuload":' + str(fetchCpuLoad()) + '}}}'
        shadow.shadowUpdate(JSONPayload, customShadowCallback_Update, 5)


def createIoTShadowClient(endpoint, thingname, keyPath, certPath, rootCaPath):
    # For certificate based connection
    myShadowClient = AWSIoTMQTTShadowClient(thingname)
    # Configurations
    # For TLS mutual authentication
    myShadowClient.configureEndpoint(
        endpoint, config.aws_iot_port())
    myShadowClient.configureCredentials(
        rootCaPath, keyPath, certPath)
    myShadowClient.configureConnectDisconnectTimeout(10)
    myShadowClient.configureMQTTOperationTimeout(5)
    return myShadowClient


def createIoTShadow(shadowClient, thingname):
    shadowClient.connect()
    # Create a device shadow instance using persistent subscription
    myDeviceShadow = shadowClient.createShadowHandlerWithName(thingname, True)
    # Shadow operations
    myDeviceShadow.shadowDelete(customShadowCallback_Delete, 5)
    myDeviceShadow.shadowRegisterDeltaCallback(
        customShadowCallback_deltaCallback)
    return myDeviceShadow


def fetchCommandLineParameters(argv):
    # get defaults
    endpoint = config.aws_iot_endpoint()
    keyPath = config.aws_iot_keypath()
    certPath = config.aws_iot_certpath()
    rootCaPath = config.aws_iot_capath()
    thingName = config.aws_iot_thingname()

    try:
        opts, args = \
            getopt.getopt(argv, "he:k:c:r:t:v", ["help", "endpoint=", "key=", "cert=", "rootCA=", "thing"])
        if len(opts) == 0:
            raise getopt.GetoptError("No input parameters!")
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print(helpInfo)
                exit(0)
            if opt in ("-e", "--endpoint"):
                endpoint = arg
            if opt in ("-r", "--rootCA"):
                rootCaPath = arg
            if opt in ("-k", "--key"):
                keyPath = arg
            if opt in ("-c", "--cert"):
                certPath = arg
            if opt in ("-t", "--thing"):
                thingName = arg
            if opt in ("-v", "--verbose"):
                logging.getLogger("core").setLevel(logging.DEBUG)

    except getopt.GetoptError:
        print(usageInfo)
        sys.exit(1)

    return endpoint, keyPath, certPath, rootCaPath, thingName


def main(argv):
    # init logger first
    logger = logging.getLogger("core")
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    endpoint, keyPath, certPath, rootCaPath, thingName = fetchCommandLineParameters(argv)

    shadowClient = createIoTShadowClient(endpoint, thingName, keyPath, certPath, rootCaPath)
    shadow = createIoTShadow(shadowClient, thingName)

    loopCount = 0
    while True:
        publishCpuLoad(shadow)
        loopCount += 1
        time.sleep(config.aws_iot_heartbeat_rate())


if __name__ == "__main__":
    main(sys.argv[1:])

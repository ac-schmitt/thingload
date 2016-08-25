# -*- coding: utf-8 -*-

import getopt
import json
import logging
import re
import subprocess
import sys
import time

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

import config

logger = None


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


def createIoTShadowClient(thingname, keyPath, certPath):
    # For certificate based connection
    myShadowClient = AWSIoTMQTTShadowClient(thingname)
    # Configurations
    # For TLS mutual authentication
    myShadowClient.configureEndpoint(
        config.aws_iot_endpoint(), config.aws_iot_port())
    myShadowClient.configureCredentials(
        config.aws_iot_capath(), keyPath, certPath)
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


def main(argv):
    keyPath = config.aws_iot_keypath()
    certPath = config.aws_iot_certpath()
    thingName = config.aws_iot_thingname()

    try:
        opts, args = getopt.getopt(argv, "k:c:t:v")
    except getopt.GetoptError:
        print("<script> -k <keyPath> -c <certPath> -t <thingName> -v")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-k":
            keyPath = arg
        elif opt == "-c":
            certPath = arg
        elif opt == "-t":
            thingName = arg
        elif opt == "-v":
            logger.setLevel(logging.DEBUG)

    shadowClient = createIoTShadowClient(thingName, keyPath, certPath)
    shadow = createIoTShadow(shadowClient, thingName)

    loopCount = 0
    while True:
        publishCpuLoad(shadow)
        loopCount += 1
        time.sleep(config.aws_iot_heartbeat_rate())


if __name__ == "__main__":
    logger = logging.getLogger("core")
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    main(sys.argv[1:])

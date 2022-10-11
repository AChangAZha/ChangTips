'''
Author: AChangAZha
Date: 2022-10-11 09:52:55
LastEditTime: 2022-10-11 10:19:31
LastEditors: AChangAZha
'''
# -*- coding: utf-8 -*-

import requests
import re
import json
import base64
import traceback
import sys


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
}
num = ""


def decrypt(PWD):
    return "decryptedPWD"


def main_handler(event, content):
    try:
        if "requestContext" not in event.keys():
            return {}
        if "queryStringParameters" not in event.keys():
            return {}
        if event["requestContext"]["path"] == "/checkUl"+num and event["requestContext"]["httpMethod"] == "POST":
            ID = event["queryStringParameters"]["ID"]
            PWD = event["queryStringParameters"]["PWD"]
            WXID = event["queryStringParameters"]["WXID"]
            if WXID == "0":
                PWD = decrypt(base64.b64decode(PWD))
            response = requests.get(
                f"https://courseapi.ulearning.cn/users/check?loginName={ID}&password={PWD}")
            if response.status_code != 200:
                traceback.print_exc()
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error = str(repr(traceback.format_exception(
                    exc_type, exc_value, exc_traceback)))
                e = {
                    "MSG": "checkUl,"+error,
                    "USER": 'Chang',
                    "AGENTID": '1000005',
                }
                requests.post(
                    "https://example.tencentcs.com/release/push"+num+"/text", data=e)
                return {"UlearningAUTHORIZATION": "error", "UlearningID2": ""}
            if json.loads(response.text)['result'] != 1:
                return {}
            session = requests.session()
            data = {
                'loginName': ID,
                'password': PWD
            }
            response = session.post(
                'https://courseapi.ulearning.cn/users/login/v2', data=data, headers=HEADERS)
            UlearningAUTHORIZATION = re.search(
                r'AUTHORIZATION=([\s\S]*?);', response.request.headers['Cookie']).group(1)
            UlearningID2 = re.search(
                r'userId%22%3A([\s\S]*?)%2C%22', response.request.headers['Cookie']).group(1)
            if WXID != '0':
                data = {
                    "WXID": WXID,
                    "UlearningAUTHORIZATION": UlearningAUTHORIZATION,
                    "UlearningID2": UlearningID2
                }
                requests.post(
                    "https://example.tencentcs.com/release/ul"+num, data=data)
            return {"UlearningAUTHORIZATION": UlearningAUTHORIZATION, "UlearningID2": UlearningID2}
        return {}
    except:
        traceback.print_exc()
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error = str(repr(traceback.format_exception(
            exc_type, exc_value, exc_traceback)))
        e = {
            "MSG": "checkUl,"+error,
            "USER": 'Chang',
            "AGENTID": '1000005',
        }
        requests.post(
            "https://example.tencentcs.com/release/push"+num+"/text", data=e)
        return {"UlearningAUTHORIZATION": "error", "UlearningID2": ""}

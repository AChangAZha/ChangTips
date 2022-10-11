# -*- coding: utf-8 -*-

import requests
import re
import json
import base64
import traceback
import sys
import js2py


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
}
HEADERS_2 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
    'Content-Type': 'application/json'
}


def decrypt(PWD):
    return "decryptedPWD"


def main_handler(event, content):
    if "requestContext" not in event.keys():
        return {}
    if "queryStringParameters" not in event.keys():
        return {}
    if event["requestContext"]["path"] == "/checkCI" and event["requestContext"]["httpMethod"] == "POST":
        try:
            ID = event["queryStringParameters"]["ID"]
            PWD = event["queryStringParameters"]["PWD"]
            OB = event["queryStringParameters"]["OB"]
            WXID = event["queryStringParameters"]["WXID"]
            if OB == "1":
                PWD = decrypt(base64.b64decode(PWD))
            session = requests.session()
            h = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42',
            }
            r = session.get('https://auth.dgut.edu.cn/authserver/login?service=https%3A%2F%2Fauth.dgut.edu.cn%2Fauthserver%2Foauth2.0%2FcallbackAuthorize%3Fclient_id%3D1021534300621787136%26redirect_uri%3Dhttps%253A%252F%252Fyqfk-daka.dgut.edu.cn%252Fnew_login%252Fdgut%26response_type%3Dcode%26client_name%3DCasOAuthClient', allow_redirects=False, headers=h)
            pwdEncryptSalt = re.search(
                r'<input type="hidden" id="pwdEncryptSalt" value="([\s\S]*?)" />', r.text).group(1)
            execution = re.search(
                r'<input type="hidden" id="execution" name="execution" value="([\s\S]*?)" />', r.text).group(1)
            eval_res, tempfile = js2py.run_file("e.js")
            PWD = tempfile.encryptPassword(PWD, pwdEncryptSalt)
            DATA = {
                'username': ID,
                'password': PWD,
                '_eventId': 'submit',
                'cllt': 'userNameLogin',
                'captcha': '',
                'lt': '',
                'dllt': 'generalLogin',
                'execution': execution
            }
            response = session.post('https://auth.dgut.edu.cn/authserver/login?service=https%3A%2F%2Fauth.dgut.edu.cn%2Fauthserver%2Foauth2.0%2FcallbackAuthorize%3Fclient_id%3D1021534300621787136%26redirect_uri%3Dhttps%253A%252F%252Fyqfk-daka.dgut.edu.cn%252Fnew_login%252Fdgut%26response_type%3Dcode%26client_name%3DCasOAuthClient', data=DATA, allow_redirects=False, headers=h)
            if response.status_code == 401:
                return {}
            if response.status_code != 302:
                traceback.print_exc()
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error = str(repr(traceback.format_exception(
                    exc_type, exc_value, exc_traceback)))
                e = {
                    "MSG": "checkCI,"+error,
                    "USER": 'Chang',
                    "AGENTID": '1000005',
                }
                requests.post(
                    "https://example.tencentcs.com/release/push/text", data=e)
                return {"DakaBEARER": "error"}
            response = session.get(response.headers.get(
                'Location'), headers=h, allow_redirects=False)
            response = session.get(
                'https://auth.dgut.edu.cn/authserver/oauth2.0/authorize?response_type=code&client_id=1021534300621787136&redirect_uri=https://yqfk-daka.dgut.edu.cn/new_login/dgut&state=yqfk',
                headers=h, allow_redirects=False)
            data = {"token": re.search(
                r'code=([\s\S]*?)&state=yqfk', response.headers.get('Location')).group(1), "state": "yqfk"}
            response = session.post(
                'https://yqfk-daka-api.dgut.edu.cn/auth', data=json.dumps(data), headers=HEADERS_2)
            DakaBEARER = json.loads(
                response.content.decode('utf-8'))['access_token']
            if WXID != '0':
                data = {
                    "WXID": WXID,
                    "DakaBEARER": DakaBEARER
                }
                requests.post(
                    "https://example.tencentcs.com/release/yqfkdaka", data=data)
            return {"DakaBEARER": DakaBEARER}
        except:
            traceback.print_exc()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error = str(repr(traceback.format_exception(
                exc_type, exc_value, exc_traceback)))
            e = {
                "MSG": "checkCI,"+error,
                "USER": 'Chang',
                "AGENTID": '1000005',
            }
            requests.post(
                "https://example.tencentcs.com/release/push/text", data=e)
            return {"DakaBEARER": "error"}
    return {}

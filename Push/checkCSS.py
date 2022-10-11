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
num = ""


def decrypt(PWD):
    return "decryptedPWD"


def main_handler(event, content):
    if "requestContext" not in event.keys():
        return {}
    if "queryStringParameters" not in event.keys():
        return {}
    if event["requestContext"]["path"] == "/checkCSS"+num and event["requestContext"]["httpMethod"] == "POST":
        try:
            ID = event["queryStringParameters"]["ID"]
            PWD = event["queryStringParameters"]["PWD"]
            WXID = event["queryStringParameters"]["WXID"]
            QB = event["queryStringParameters"]["QB"]
            OB = event["queryStringParameters"]["OB"]
            if OB == "1":
                PWD = decrypt(base64.b64decode(PWD))
            PWD_ = PWD
            session = requests.session()
            h = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42',
            }
            r = session.get('https://auth.dgut.edu.cn/authserver/login?service=https%3A%2F%2Fauth.dgut.edu.cn%2Fauthserver%2Foauth2.0%2FcallbackAuthorize%3Fclient_id%3D971734811307233280%26redirect_uri%3Dhttps%253A%252F%252Fhw.dgut.edu.cn%252Fnewlogin%26response_type%3Dcode%26client_name%3DCasOAuthClient', allow_redirects=False, headers=h)
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
            response = session.post('https://auth.dgut.edu.cn/authserver/login?service=https://auth.dgut.edu.cn/authserver/oauth2.0/callbackAuthorize?client_id=971734811307233280&redirect_uri=https%3A%2F%2Fhw.dgut.edu.cn%2Fnewlogin&response_type=code&client_name=CasOAuthClient', data=DATA, allow_redirects=False, headers=h)
            if response.status_code == 401:
                return {}
            if response.status_code != 302:
                traceback.print_exc()
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error = str(repr(traceback.format_exception(
                    exc_type, exc_value, exc_traceback)))
                e = {
                    "MSG": "checkCSS,"+error,
                    "USER": 'Chang',
                    "AGENTID": '1000005',
                }
                requests.post(
                    "https://example.tencentcs.com/release/push"+num+"/text", data=e)
                return {"HomeworkSESSION": "error", "DakaBEARER": ""}
            response = session.get(response.headers.get(
                'Location'), headers=h, allow_redirects=False)
            response = session.get(
                'https://auth.dgut.edu.cn/authserver/oauth2.0/authorize?response_type=code&client_id=971734811307233280&redirect_uri=https://hw.dgut.edu.cn/newlogin', headers=h, allow_redirects=False)
            response = session.get(response.headers.get(
                'Location'), headers=h, allow_redirects=False)
            DakaBEARER = ""
            HomeworkSESSION = re.search(
                r"SESSION=([\s\S]*?);", str(response.headers.get('Set-Cookie'))).group(1)
            if QB == "1":
                data = {
                    "ID": ID,
                    "PWD": PWD_,
                    "WXID": "0",
                    "OB": "0"
                }
                DakaBEARER = json.loads(requests.post(
                    "https://example.tencentcs.com/release/checkCI"+num, data=data).text).get('BEARER')
                if DakaBEARER == "error":
                    traceback.print_exc()
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    error = str(repr(traceback.format_exception(
                        exc_type, exc_value, exc_traceback)))
                    e = {
                        "MSG": "checkCSS-checkCI,"+error,
                        "USER": 'Chang',
                        "AGENTID": '1000005',
                    }
                    requests.post(
                        "https://example.tencentcs.com/release/push"+num+"/text", data=e)
                    return {"HomeworkSESSION": "error", "DakaBEARER": DakaBEARER}
                if WXID != '0':
                    data = {
                        "WXID": WXID,
                        "DakaBEARER": DakaBEARER
                    }
                    requests.post(
                        "https://example.tencentcs.com/release/yqfkdaka"+num, data=data)
            if WXID != '0':
                data = {
                    "WXID": WXID,
                    "HomeworkSESSION": HomeworkSESSION
                }
                requests.post(
                    "https://example.tencentcs.com/release/hwcss"+num, data=data)
            return {"HomeworkSESSION": HomeworkSESSION, "DakaBEARER": DakaBEARER}
        except:
            traceback.print_exc()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error = str(repr(traceback.format_exception(
                exc_type, exc_value, exc_traceback)))
            e = {
                "MSG": "checkCSS,"+error,
                "USER": 'Chang',
                "AGENTID": '1000005',
            }
            requests.post(
                "https://example.tencentcs.com/release/push"+num+"/text", data=e)
            return {"HomeworkSESSION": "error", "DakaBEARER": DakaBEARER}
    return {}

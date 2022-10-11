# -*- coding: utf8 -*-
import json
import requests
import pymysql
import traceback
import sys
import time
try:
    DB = pymysql.connect(host='localhost',
                         port=0000,
                         user='user',
                         password='password',
                         database='database')
except:
    traceback.print_exc()
    exc_type, exc_value, exc_traceback = sys.exc_info()
    error = str(repr(traceback.format_exception(
        exc_type, exc_value, exc_traceback)))
    e = {
        "MSG": "yqfkdaka,DB,"+error,
        "USER": 'Chang',
        "AGENTID": '1000005',
    }
    requests.post(
        "https://example.tencentcs.com/release/push/text", data=e)


def daka(wxID, Bind=False, DakaBEARER="", MSG="让我看看是谁还没打卡！"):
    DB.ping(reconnect=True)
    cursor = DB.cursor()
    if not DakaBEARER:
        sql = "SELECT DakaBEARER FROM user WHERE WeChatName='%s'" % (wxID)
        DB.ping(reconnect=True)
        cursor.execute(sql)
        DakaBEARER = cursor.fetchone()[0]
    DakaBEARER = "Bearer "+DakaBEARER
    headers = {
        'Authorization': DakaBEARER
    }
    session = requests.session()
    try:
        state = json.loads(session.get(
            'https://yqfk-daka-api.dgut.edu.cn/record/', headers=headers).text)
        if "hide_submit" not in state.keys():
            sql = "SELECT StudentNumber FROM user WHERE WeChatName='%s'" % (
                wxID)
            DB.ping(reconnect=True)
            cursor.execute(sql)
            ID = cursor.fetchone()[0]
            sql = "SELECT StudentPassword FROM user WHERE WeChatName='%s'" % (
                wxID)
            DB.ping(reconnect=True)
            cursor.execute(sql)
            PWD = cursor.fetchone()[0]
            data = {
                "ID": ID,
                "PWD": PWD,
                "WXID": "0",
                "OB": "1"
            }
            response = requests.post(
                f"https://example.tencentcs.com/release/checkCI", data=data)
            response = json.loads(response.text)
            if "DakaBEARER" not in response.keys():
                sql = "UPDATE user SET DakaBEARER='' WHERE WeChatName='%s'" % (
                    wxID)
                DB.ping(reconnect=True)
                cursor.execute(sql)
                DB.commit()
                data = {
                    "title": '获取信息失败',
                    "message": '无法获取您的疫情打卡信息，已为您暂停服务。<br><br>若您修改了所绑定账号的密码，请点击下方“绑定账号”菜单以更新密码。<br><br>若您并未修改所绑定账号的密码，请联系开发者解决。',
                    "url": 'https://yqfk-daka.dgut.edu.cn/',
                    "user": wxID,
                    "agentid": '1000003',
                }
                requests.post(
                    "https://example.tencentcs.com/release/push/textcard", data=data)
                cursor.close()
                time.sleep(3)
                return {"success": 0}
            elif response["DakaBEARER"] != "error":
                sql = "UPDATE user SET DakaBEARER='%s' WHERE WeChatName='%s'" % (
                    response["DakaBEARER"], wxID)
                DB.ping(reconnect=True)
                cursor.execute(sql)
                DB.commit()
                headers["Authorization"] = "Bearer "+response["DakaBEARER"]
                state = json.loads(session.get(
                    'https://yqfk-daka-api.dgut.edu.cn/record/', headers=headers).text)
            else:
                raise Exception("error")
    except:
        traceback.print_exc()
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error = str(repr(traceback.format_exception(
            exc_type, exc_value, exc_traceback)))
        e = {
            "MSG": "yqfkdaka,connect,"+error,
            "USER": 'Chang',
            "AGENTID": '1000005',
        }
        requests.post(
            "https://example.tencentcs.com/release/push/text", data=e)
        cursor.close()
        time.sleep(3)
        return {"success": 0}
    data = {
        "url": 'https://yqfk-daka.dgut.edu.cn/',
        "user": wxID,
        "agentid": '1000003',
    }
    if state["hide_submit"] == True:
        try:
            sql = "INSERT INTO yqfkdaka VALUES ('%s')" % (wxID)
            DB.ping(reconnect=True)
            cursor.execute(sql)
            DB.commit()
        except:
            pass
        if Bind:
            data['title'] = '绑定成功'
            data["message"] = state["message"],
            requests.post(
                "https://example.tencentcs.com/release/push/textcard", data=data)
    elif state["hide_submit"] == False:
        data["title"] = '打卡提醒',
        data["message"] = f'{MSG}<br>点击卡片可快速进入打卡页面。',
        if Bind:
            data['title'] = '绑定成功'
        requests.post(
            "https://example.tencentcs.com/release/push/textcard", data=data)
    cursor.close()
    time.sleep(3)
    return {"success": 1}


def main_handler(event, context):
    if "Type" in event.keys():
        if event["Type"] == "Timer":
            DB.ping(reconnect=True)
            cursor = DB.cursor()
            if event["TriggerName"] == "Clear":
                sql = "TRUNCATE TABLE yqfkdaka"
                DB.ping(reconnect=True)
                cursor.execute(sql)
                DB.commit()
                r = requests.get(
                    f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=exampleCorpid&corpsecret=exampleCorpsecret")
                ACCESS_TOKEN = json.loads(r.text)['access_token']
                r = requests.get(
                    f"https://qyapi.weixin.qq.com/cgi-bin/user/simplelist?access_token={ACCESS_TOKEN}&department_id=1")
                userlist = json.loads(r.text)['userlist']
                sql = "SELECT NAME FROM cisettings_ci WHERE zero = '0'"
                DB.ping(reconnect=True)
                cursor.execute(sql)
                rows = cursor.fetchall()
                for user in userlist:
                    zero = 1
                    for row in rows:
                        if user["userid"] == row[0]:
                            zero = 0
                            break
                    if zero == 1:
                        data = {
                            "url": 'https://yqfk-daka.dgut.edu.cn/',
                            "user": user["userid"],
                            "agentid": '1000003',
                            "title": "打卡提醒",
                        }
                        data["message"] = f'新的一天开始啦，记得打卡！<br>点击卡片可快速进入打卡页面。',
                        requests.post(
                            "https://example.tencentcs.com/release/push/textcard", data=data)
            else:
                if event["TriggerName"] == "Tips23":
                    sql = "SELECT user.WeChatName FROM user, cisettings_ci WHERE user.NAME = cisettings_ci.NAME AND user.WeChatName NOT IN (SELECT WeComID FROM yqfkdaka) AND DakaBEARER <> ''"
                else:
                    sql = "SELECT user.WeChatName FROM user, cisettings_ci WHERE user.NAME = cisettings_ci.NAME AND user.WeChatName NOT IN (SELECT WeComID FROM yqfkdaka) AND DakaBEARER <> '' AND continued = '1'"
                DB.ping(reconnect=True)
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    daka(row[0], MSG=event["Message"])
            cursor.close()
            DB.close()
    if "requestContext" not in event.keys():
        return {}
    if "queryStringParameters" not in event.keys():
        return {}
    if event["requestContext"]["path"] == "/yqfkdaka" and event["requestContext"]["httpMethod"] == "POST":
        WXID = event["queryStringParameters"]["WXID"]
        DakaBEARER = event["queryStringParameters"]["DakaBEARER"]
        j = daka(WXID, True, DakaBEARER=DakaBEARER)
        DB.close()
        return j

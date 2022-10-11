# -*- coding: utf8 -*-
from copy import deepcopy
import json
import time
import requests
from functools import cmp_to_key
import pymysql
import traceback
import sys
DB = pymysql.connect(host='localhost',
                     port=0000,
                     user='user',
                     password='password',
                     database='database')
type = {
    1: "作业",
    2: "互评",
    3: "讨论",
    4: "长期讨论",
}
num = ""
now = time.time()


def ULEARNING(wxID):
    DB.ping(reconnect=True)
    cursor = DB.cursor()
    sql = "SELECT UlearningAUTHORIZATION FROM user WHERE WeChatName='%s'" % (
        wxID)
    DB.ping(reconnect=True)
    cursor.execute(sql)
    UlearningAUTHORIZATION = cursor.fetchone()[0]
    sql = "SELECT UlearningID2 FROM user WHERE WeChatName='%s'" % (wxID)
    DB.ping(reconnect=True)
    cursor.execute(sql)
    UlearningID2 = cursor.fetchone()[0]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
        'Authorization': UlearningAUTHORIZATION
    }
    session = requests.session()
    startDate = time.strftime("%Y-%m-%d", time.localtime(now+28800))
    Tcalendar = json.loads(session.get(
        f'https://courseapi.ulearning.cn/activitycalendar?startDate={startDate}&endDate={startDate}&lang=zh', headers=headers).text)

    startDate = "2022-08-26"
    endDate = "2023-02-19"

    if not Tcalendar.get("total"):
        sql = "SELECT UlearningID FROM user WHERE WeChatName='%s'" % (wxID)
        DB.ping(reconnect=True)
        cursor.execute(sql)
        ID = cursor.fetchone()[0]
        sql = "SELECT UlearningPassword FROM user WHERE WeChatName='%s'" % (
            wxID)
        DB.ping(reconnect=True)
        cursor.execute(sql)
        PWD = cursor.fetchone()[0]
        if not PWD or not ID:
            cursor.close()
            return {"error": "1"}
        data = {
            "ID": ID,
            "PWD": PWD,
            "WXID": "0",
        }
        response = requests.post(
            f"https://example.tencentcs.com/release/checkUl"+num, data=data)
        response = json.loads(response.text)
        if "UlearningAUTHORIZATION" not in response.keys():
            sql = "UPDATE user SET UlearningAUTHORIZATION='' WHERE WeChatName='%s'" % (
                wxID)
            DB.ping(reconnect=True)
            cursor.execute(sql)
            DB.commit()
            cursor.close()
            data = {
                "title": '获取信息失败',
                "message": '无法获取您的优学院账号信息，已为您暂停服务。<br><br>若您修改了所绑定账号的密码，请点击下方“绑定账号”菜单以更新密码。若您在7天内没有更新，系统将自动取消绑定您的账号并删除您所绑定的账号信息。<br><br>若您并未修改所绑定账号的密码，请联系开发者解决。',
                "url": 'https://courseweb.ulearning.cn/ulearning/index.html#/index/courseList',
                "user": wxID,
                "agentid": '1000002',
            }
            requests.post(
                "https://example.tencentcs.com/release/push"+num+"/textcard", data=data)
            return {}
        if "UlearningAUTHORIZATION" in response.keys() and response["UlearningAUTHORIZATION"] != "error":
            sql = "UPDATE user SET UlearningAUTHORIZATION='%s' WHERE WeChatName='%s'" % (
                response["UlearningAUTHORIZATION"], wxID)
            DB.ping(reconnect=True)
            cursor.execute(sql)
            DB.commit()
            headers["AUTHORIZATION"] = response["UlearningAUTHORIZATION"]
        else:
            traceback.print_exc()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error = str(repr(traceback.format_exception(
                exc_type, exc_value, exc_traceback)))
            e = {
                "MSG": "getullist,"+error,
                "USER": 'Chang',
                "AGENTID": '1000005',
            }
            cursor.close()
            requests.post(
                "https://example.tencentcs.com/release/push"+num+"/text", data=e)
            return {}

    cursor.close()
    calendar = json.loads(session.get(
        f'https://courseapi.ulearning.cn/activitycalendar?startDate={startDate}&endDate={endDate}&lang=zh', headers=headers).text)
    if not calendar.get("courseList"):
        return {}
    notSubmitted = getPlan(
        calendar["courseList"], session, now, headers, UlearningID2)
    if notSubmitted:
        notSubmitted = sorted(notSubmitted, key=cmp_to_key(cmp_deadline))
        res = {}
        ulList = []
        for recently in notSubmitted:
            one = {}
            one["courseName"] = recently["courseName"]
            one["homeworkName"] = recently["homeworkTitle"]
            deadlineDate = recently["endTime"]
            one["week"], one["Time"] = dayOfTheWeek(deadlineDate)
            one["Type"] = type[recently["type"]]
            ulList.append(one)
        res["list"] = ulList
        return res
    else:
        return {}


def main_handler(event, context):
    try:
        if "requestContext" not in event.keys():
            return {}
        if "queryStringParameters" not in event.keys():
            return {}
        if event["requestContext"]["path"] == "/getullist"+num and event["requestContext"]["httpMethod"] == "POST":
            WXID = event["queryStringParameters"]["wxid"]
            json = ULEARNING(WXID)
            DB.close()
            return json
    except:
        traceback.print_exc()
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error = str(repr(traceback.format_exception(
            exc_type, exc_value, exc_traceback)))
        e = {
            "MSG": "getullist,"+error,
            "USER": 'Chang',
            "AGENTID": '1000005',
        }
        requests.post(
            "https://example.tencentcs.com/release/push"+num+"/text", data=e)
        return {}


def cmp_deadline(hw_1, hw_2):
    if hw_1["endTime"] > hw_2["endTime"]:
        return 1
    elif hw_1["endTime"] < hw_2["endTime"]:
        return -1
    else:
        if hw_1["startTime"] > hw_2["startTime"]:
            return 1
        else:
            return -1


def dayOfTheWeek(deadlineDate):
    week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    stime = time.localtime(deadlineDate+28800)
    date = time.strftime("%m-%d %H:%M", stime)
    dayOfTheWeek = " "+week_list[stime.tm_wday]
    if stime.tm_hour >= 0 and stime.tm_hour <= 6:
        dayOfTheWeek = " "+week_list[stime.tm_wday]+"凌晨" + "<br>注意！该任务需要在 " + \
            week_list[stime.tm_wday-1]+"晚上 或 " + \
            week_list[stime.tm_wday]+"凌晨 完成。"
    elif stime.tm_hour > 6 and stime.tm_hour <= 12:
        dayOfTheWeek = " "+week_list[stime.tm_wday]+"早上"
    elif stime.tm_hour > 12 and stime.tm_hour < 18:
        dayOfTheWeek = " "+week_list[stime.tm_wday]+"下午"
    elif stime.tm_hour >= 18 and stime.tm_hour <= 23:
        dayOfTheWeek = " "+week_list[stime.tm_wday]+"晚上"
    return dayOfTheWeek, date


def getPlan(courseList, session, nowTime, headers, UlearningID2):
    HW = []
    for i in courseList:
        ocId = i["ocId"]
        hw = json.loads(session.get(
            f'https://courseapi.ulearning.cn/homeworks/student/v2?ocId={ocId}&pn=1&ps=100&lang=zh', headers=headers).text)
        if hw.get('homeworkList'):
            for j in hw['homeworkList']:
                one = {}
                p = False
                if j["state"] == 0 or j["state"] == 1 or j["state"] == 2:
                    if j.get("peerReviewTime") and j["peerReviewTime"]/1000-nowTime > 0:
                        p = True
                    if j["endTime"]/1000-nowTime > 0 or p == True:
                        one["homeworkTitle"] = j["homeworkTitle"]
                        one["courseName"] = i["courseName"]
                        if j["state"] == 0 and j["endTime"]/1000-nowTime > 0:
                            one["endTime"] = j["endTime"]/1000
                            one["startTime"] = j["startTime"]/1000
                            one["type"] = 1
                            HW.append(one)
                        if p:
                            p = False
                            if j["state"] == 2:
                                HWID = j["id"]
                                HP = json.loads(session.get(
                                    f'https://homeworkapi.ulearning.cn/stuHomework/peerReviewHomeworkDatil/{HWID}/{UlearningID2}', headers=headers).text)
                                for k in HP["result"]:
                                    if k["score"] is None:
                                        p = True
                                        break
                            if p:
                                one = deepcopy(one)
                                one["startTime"] = j["endTime"]/1000
                                one["endTime"] = j["peerReviewTime"]/1000
                                one["type"] = 2
                                HW.append(one)
        disc = json.loads(session.get(
            f'https://courseapi.ulearning.cn/forum/student/{ocId}/{UlearningID2}?pn=1&ps=100&lang=zh', headers=headers).text)
        if disc.get('studentForumDiscussionList'):
            for k in disc['studentForumDiscussionList']:
                one = {}
                if k["myPostCount"] == 0:
                    if k.get("endTime"):
                        if k["endTime"]/1000-nowTime > 0:
                            one["endTime"] = k["endTime"]/1000
                            one["startTime"] = k["startTime"]/1000
                            one["homeworkTitle"] = k["title"]
                            one["courseName"] = i["courseName"]
                            one["type"] = 3
                            HW.append(one)
                    else:
                        one["endTime"] = nowTime+28800+86400*180
                        one["startTime"] = k["createDate"]/1000
                        one["homeworkTitle"] = k["title"]
                        one["courseName"] = i["courseName"]
                        one["type"] = 4
                        HW.append(one)
    return HW

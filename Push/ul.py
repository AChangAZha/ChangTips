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


def ULEARNING(wxID, now, Bind=False, Create=False, Morning=False, Night=False, Preview0=False, Week=False, TwoDays=False, Exam=False, Exam_2=False, UlearningAUTHORIZATION="", UlearningID2=""):
    DB.ping(reconnect=True)
    cursor = DB.cursor()
    try:
        if not UlearningAUTHORIZATION:
            sql = "SELECT UlearningAUTHORIZATION FROM user WHERE WeChatName='%s'" % (
                wxID)
            DB.ping(reconnect=True)
            cursor.execute(sql)
            UlearningAUTHORIZATION = cursor.fetchone()[0]
        if not UlearningID2:
            sql = "SELECT UlearningID2 FROM user WHERE WeChatName='%s'" % (
                wxID)
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

        endDate = "2023-02-19"

        if Tcalendar.get("total") is None:
            sql = "SELECT UlearningID FROM user WHERE WeChatName='%s'" % (wxID)
            DB.ping(reconnect=True)
            cursor.execute(sql)
            ID = cursor.fetchone()[0]
            sql = "SELECT UlearningPassword FROM user WHERE WeChatName='%s'" % (
                wxID)
            DB.ping(reconnect=True)
            cursor.execute(sql)
            PWD = cursor.fetchone()[0]
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
                    "message": '无法获取您的优学院账号信息，已为您暂停服务。<br><br>若您修改了所绑定账号的密码，请点击下方“绑定账号”菜单以更新密码。<br><br>若您并未修改所绑定账号的密码，请忽略此条消息并联系开发者解决。',
                    "url": 'https://courseweb.ulearning.cn/ulearning/index.html#/index/courseList',
                    "user": wxID,
                    "agentid": '1000002',
                }
                requests.post(
                    "https://example.tencentcs.com/release/push"+num+"/textcard", data=data)
                return {"success": 0}
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
                    "MSG": "ul,"+error,
                    "USER": 'Chang',
                    "AGENTID": '1000005',
                }
                requests.post(
                    "https://example.tencentcs.com/release/push"+num+"/text", data=e)
                cursor.close()
                return {"success": 0}
        cursor.close()
        data = {
            "url": 'https://courseweb.ulearning.cn/ulearning/index.html#/index/courseList',
            "user": wxID,
            "agentid": '1000002',
        }
        if Bind:
            data['title'] = '绑定成功'
            startDate = "2022-08-26"
            calendar = json.loads(session.get(
                f'https://courseapi.ulearning.cn/activitycalendar?startDate={startDate}&endDate={endDate}&lang=zh', headers=headers).text)
            if not calendar.get("courseList"):
                data["message"] = "最近没有需要完成的任务。",
                requests.post(
                    "https://example.tencentcs.com/release/push"+num+"/textcard", data=data)
                return {}
            notSubmitted = getPlan(
                calendar["courseList"], session, now, headers, UlearningID2)
            if notSubmitted:
                notSubmitted = sorted(
                    notSubmitted, key=cmp_to_key(cmp_deadline))
                recently = notSubmitted[0]
                courseName = recently["courseName"]
                homeworkName = recently["homeworkTitle"]
                deadlineDate = recently["endTime"]
                week, Time = dayOfTheWeek(deadlineDate)
                Type = type[recently["type"]]
                ME = ""
                if recently["type"] == 2:
                    ME = "<br>请注意该作业需要完成互评！"
                data["message"] = f"最近需要完成的任务：<br>课程名称：{courseName}<br>{Type}：{homeworkName}<br>截止时间：{Time}"+week+ME
            else:
                data["message"] = "最近没有需要完成的任务。",
            requests.post(
                "https://example.tencentcs.com/release/push"+num+"/textcard", data=data)
        if Create:
            title = '新任务'
            calendar = json.loads(session.get(
                f'https://courseapi.ulearning.cn/activitycalendar?startDate={startDate}&endDate={endDate}&lang=zh', headers=headers).text)
            if not calendar.get("courseList"):
                return {}
            notSubmitted = getPlan(
                calendar["courseList"], session, now, headers, UlearningID2)
            newCreate = []
            for i in notSubmitted:
                new = now-i["startTime"]
                if new <= 86410:
                    newCreate.append(i)
            if not newCreate:
                return {}
            newCreate = sorted(newCreate, key=cmp_to_key(
                cmp_deadline), reverse=True)
            for i in newCreate:
                if i["type"] == 2:
                    continue
                courseName = i["courseName"]
                homeworkName = i["homeworkTitle"]
                data["title"] = "【" + title+"】"+courseName+"  "+homeworkName
                deadlineDate = i["endTime"]
                Type = type[i["type"]]
                week, Time = dayOfTheWeek(deadlineDate)
                data["message"] = f"老师今日发布了新任务：<br>课程名称：{courseName}<br>{Type}：{homeworkName}<br>截止时间：{Time}"
                requests.post(
                    "https://example.tencentcs.com/release/push"+num+"/textcard", data=data)
        elif Exam:
            startDate = "2022-08-26"
            endDate = time.strftime(
                "%Y-%m-%d", time.localtime(now+28800))
            calendar = json.loads(session.get(
                f'https://courseapi.ulearning.cn/activitycalendar?startDate={startDate}&endDate={endDate}&lang=zh', headers=headers).text)
            if not calendar["activityList"]:
                return {}
            Title = '考试提醒'
            for i in calendar["activityList"]:
                if i["activityType"] == 5:
                    if i["endTime"]/1000 < now:
                        continue
                    if i["beginTime"]/1000 - now > 86400:
                        continue
                    if i["beginTime"]/1000 < now and i["endTime"]/1000 - now > 86400:
                        continue
                    courseName = i["courseName"]
                    title = i["title"]
                    data["title"] = "【" + Title+"】"+courseName+"  "+title
                    endTime = i["endTime"]/1000
                    beginTime = i["beginTime"]/1000
                    bWeek, bTime = dayOfTheWeek(beginTime)
                    eWeek, eTime = dayOfTheWeek(endTime)
                    data["message"] = f"课程名称：{courseName}<br>考试名称：{title}<br>开始时间：{bTime}<br>结束时间：{eTime}"+eWeek
                    requests.post(
                        "https://example.tencentcs.com/release/push"+num+"/textcard", data=data)
        elif Exam_2:
            startDate = "2022-08-26"
            endDate = time.strftime(
                "%Y-%m-%d", time.localtime(now+28800+86400))
            calendar = json.loads(session.get(
                f'https://courseapi.ulearning.cn/activitycalendar?startDate={startDate}&endDate={endDate}&lang=zh', headers=headers).text)
            if not calendar["activityList"]:
                return {}
            Title = '考试提醒'
            for i in calendar["activityList"]:
                if i["activityType"] == 5:
                    if i["endTime"]/1000 < now:
                        continue
                    if i["beginTime"]/1000 - now > 86400+46200:
                        continue
                    if i["beginTime"]/1000 < now and i["endTime"]/1000 - now > 86400+46200:
                        continue
                    courseName = i["courseName"]
                    title = i["title"]
                    data["title"] = "【" + Title+"】"+courseName+"  "+title
                    endTime = i["endTime"]/1000
                    beginTime = i["beginTime"]/1000
                    bWeek, bTime = dayOfTheWeek(beginTime)
                    eWeek, eTime = dayOfTheWeek(endTime)
                    data["message"] = f"课程名称：{courseName}<br>考试名称：{title}<br>开始时间：{bTime}<br>结束时间：{eTime}"+eWeek
                    requests.post(
                        "https://example.tencentcs.com/release/push"+num+"/textcard", data=data)
        elif Morning:
            title = '今日截止'
            cutOff = []
            startDate = "2022-08-26"
            endDate = time.strftime(
                "%Y-%m-%d", time.localtime(now+28800))
            calendar = json.loads(session.get(
                f'https://courseapi.ulearning.cn/activitycalendar?startDate={startDate}&endDate={startDate}&lang=zh', headers=headers).text)
            if not calendar.get("courseList"):
                return {}
            notSubmitted = getPlan(
                calendar["courseList"], session, now, headers, UlearningID2)
            for i in notSubmitted:
                dl = i["endTime"]-now
                if dl <= 40810:
                    cutOff.append(i)
            if not cutOff:
                return {}
            cutOff = sorted(cutOff, key=cmp_to_key(
                cmp_deadline))
            for i in cutOff:
                courseName = i["courseName"]
                homeworkName = i["homeworkTitle"]
                data["title"] = "【" + title+"】"+courseName+"  "+homeworkName
                deadlineDate = i["endTime"]
                Type = type[i["type"]]
                week, Time = dayOfTheWeek(deadlineDate)
                ME = ""
                if i["type"] == 2:
                    ME = "<br>请注意该作业需要完成互评！"
                data["message"] = f"以下任务需要在今日18:20前完成：<br>课程名称：{courseName}<br>{Type}：{homeworkName}<br>截止时间：{Time}" + week + ME
                requests.post(
                    "https://example.tencentcs.com/release/push"+num+"/textcard", data=data)
        elif Night:
            title = '今晚截止'
            cutOff = []
            startDate = "2022-08-26"
            endDate = time.strftime(
                "%Y-%m-%d", time.localtime(now+28800+86400))
            calendar = json.loads(session.get(
                f'https://courseapi.ulearning.cn/activitycalendar?startDate={startDate}&endDate={endDate}&lang=zh', headers=headers).text)
            if not calendar.get("courseList"):
                return {}
            notSubmitted = getPlan(
                calendar["courseList"], session, now, headers, UlearningID2)
            for i in notSubmitted:
                dl = i["endTime"]-now
                if dl <= 45610:
                    cutOff.append(i)
            if not cutOff:
                return {}
            cutOff = sorted(cutOff, key=cmp_to_key(
                cmp_deadline))
            for i in cutOff:
                courseName = i["courseName"]
                homeworkName = i["homeworkTitle"]
                data["title"] = "【" + title+"】"+courseName+"  "+homeworkName
                deadlineDate = i["endTime"]
                Type = type[i["type"]]
                week, Time = dayOfTheWeek(deadlineDate)
                ME = ""
                if i["type"] == 2:
                    ME = "<br>请注意该作业需要完成互评！"
                data["message"] = f"以下任务需要今日晚上或明日凌晨前完成：<br>课程名称：{courseName}<br>{Type}：{homeworkName}<br>截止时间：{Time}" + week+ME
                requests.post(
                    "https://example.tencentcs.com/release/push"+num+"/textcard", data=data)
        elif Preview0:
            title = '明晚截止'
            cutOff = []
            startDate = "2022-08-26"
            endDate = time.strftime(
                "%Y-%m-%d", time.localtime(now+28800+86400*2))
            calendar = json.loads(session.get(
                f'https://courseapi.ulearning.cn/activitycalendar?startDate={startDate}&endDate={endDate}&lang=zh', headers=headers).text)
            if not calendar.get("courseList"):
                return {}
            notSubmitted = getPlan(
                calendar["courseList"], session, now, headers, UlearningID2)
            for i in notSubmitted:
                dl = i["endTime"]-now
                if dl >= 107930 and dl <= 133150:
                    cutOff.append(i)
            if not cutOff:
                return {}
            cutOff = sorted(cutOff, key=cmp_to_key(
                cmp_deadline))
            for i in cutOff:
                courseName = i["courseName"]
                homeworkName = i["homeworkTitle"]
                data["title"] = "【" + title+"】"+courseName+"  "+homeworkName
                deadlineDate = i["endTime"]
                week, Time = dayOfTheWeek(deadlineDate)
                Type = type[i["type"]]
                ME = ""
                if i["type"] == 2:
                    ME = "<br>请注意该作业需要完成互评！"
                data["message"] = f"以下任务需要明日晚上或后天凌晨前完成：<br>课程名称：{courseName}<br>{Type}：{homeworkName}<br>截止时间：{Time}" + week+ME
                requests.post(
                    "https://example.tencentcs.com/release/push"+num+"/textcard", data=data)
        elif Week:
            title = '本周计划'
            plan = []
            startDate = "2022-08-26"
            endDate = time.strftime(
                "%Y-%m-%d", time.localtime(now+28800+86400*7))
            calendar = json.loads(session.get(
                f'https://courseapi.ulearning.cn/activitycalendar?startDate={startDate}&endDate={endDate}&lang=zh', headers=headers).text)
            notSubmitted = getPlan(
                calendar["courseList"], session, now, headers, UlearningID2)
            for i in notSubmitted:
                dl = i["endTime"]-now
                if dl <= 604810:
                    plan.append(i)
            if not plan:
                return {}
            plan = sorted(plan, key=cmp_to_key(
                cmp_deadline))
            for i in plan:
                courseName = i["courseName"]
                homeworkName = i["homeworkTitle"]
                data["title"] = "【" + title+"】"+courseName+"  "+homeworkName
                deadlineDate = i["endTime"]
                Type = type[i["type"]]
                week, Time = dayOfTheWeek(deadlineDate)
                ME = ""
                if i["type"] == 2:
                    ME = "<br>请注意该作业需要完成互评！"
                data["message"] = f"本周（下周一7:00前）需要完成的任务：<br>课程名称：{courseName}<br>{Type}：{homeworkName}<br>截止时间：{Time}" + week+ME
                requests.post(
                    "https://example.tencentcs.com/release/push"+num+"/textcard", data=data)
        elif TwoDays:
            title = '明天截止'
            plan = []
            startDate = "2022-08-26"
            endDate = time.strftime(
                "%Y-%m-%d", time.localtime(now+28800+86400*2))
            calendar = json.loads(session.get(
                f'https://courseapi.ulearning.cn/activitycalendar?startDate={startDate}&endDate={endDate}&lang=zh', headers=headers).text)
            if not calendar.get("courseList"):
                return {}
            notSubmitted = getPlan(
                calendar["courseList"], session, now, headers, UlearningID2)
            for i in notSubmitted:
                dl = i["endTime"]-now
                if dl >= 46790 and dl <= 133210:
                    plan.append(i)
            if not plan:
                return {}
            plan = sorted(plan, key=cmp_to_key(
                cmp_deadline))
            for i in plan:
                courseName = i["courseName"]
                homeworkName = i["homeworkTitle"]
                data["title"] = "【" + title+"】"+courseName+"  "+homeworkName
                deadlineDate = i["endTime"]
                week, Time = dayOfTheWeek(deadlineDate)
                Type = type[i["type"]]
                ME = ""
                if i["type"] == 2:
                    ME = "<br>请注意该作业需要完成互评！"
                data["message"] = f"明天前需要完成的任务：<br>课程名称：{courseName}<br>{Type}：{homeworkName}<br>截止时间：{Time}" + week+ME
                requests.post(
                    "https://example.tencentcs.com/release/push"+num+"/textcard", data=data)
        return {"success": 1}
    except:
        traceback.print_exc()
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error = str(repr(traceback.format_exception(
            exc_type, exc_value, exc_traceback)))
        e = {
            "MSG": "ul,"+error,
            "USER": 'Chang',
            "AGENTID": '1000005',
        }
        requests.post(
            "https://example.tencentcs.com/release/push"+num+"/text", data=e)
        return {"success": 0}


def main_handler(event, context):
    now = time.time()
    if "Type" in event.keys():
        if event["Type"] == "Timer":
            DB.ping(reconnect=True)
            cursor = DB.cursor()
            sql = "SELECT WeChatName FROM user WHERE UlearningAUTHORIZATION <>''"
            DB.ping(reconnect=True)
            cursor.execute(sql)
            rows = cursor.fetchall()
            startDate = time.strftime("%Y-%m-%d", time.localtime(now+28800))
            now = nowtime(event, startDate)
            for row in rows:
                if event["TriggerName"] == "Create":
                    ULEARNING(row[0], now, Create=True)
                if event["TriggerName"] == "Morning":
                    ULEARNING(row[0], now, Morning=True)
                if event["TriggerName"] == "Night":
                    ULEARNING(row[0], now, Night=True)
                if event["TriggerName"] == "Preview0":
                    ULEARNING(row[0], now, Preview0=True)
                if event["TriggerName"] == "Week":
                    ULEARNING(row[0], now, Week=True)
                if event["TriggerName"] == "TwoDays":
                    ULEARNING(row[0], now, TwoDays=True)
                if event["TriggerName"] == "Exam":
                    ULEARNING(row[0], now, Exam=True)
                if event["TriggerName"] == "Exam_2":
                    ULEARNING(row[0], now, Exam_2=True)
            cursor.close()
            DB.close()
    if "requestContext" not in event.keys():
        return {}
    if "queryStringParameters" not in event.keys():
        return {}
    if event["requestContext"]["path"] == "/ul"+num and event["requestContext"]["httpMethod"] == "POST":
        WXID = event["queryStringParameters"]["WXID"]
        UlearningAUTHORIZATION = event["queryStringParameters"]["UlearningAUTHORIZATION"]
        UlearningID2 = event["queryStringParameters"]["UlearningID2"]
        json = ULEARNING(
            WXID, int(now), Bind=True, UlearningAUTHORIZATION=UlearningAUTHORIZATION, UlearningID2=UlearningID2)
        DB.close()
        return json


def nowtime(event, startDate):
    if event["TriggerName"] == "Create":
        now = int(time.mktime(time.strptime(
            startDate+" 23:00", '%Y-%m-%d %H:%M'))-28800)
    if event["TriggerName"] == "Morning":
        now = int(time.mktime(time.strptime(
            startDate+" 07:00", '%Y-%m-%d %H:%M'))-28800)
    if event["TriggerName"] == "Night":
        now = int(time.mktime(time.strptime(
            startDate+" 18:20", '%Y-%m-%d %H:%M'))-28800)
    if event["TriggerName"] == "Preview0":
        now = int(time.mktime(time.strptime(
            startDate+" 18:01", '%Y-%m-%d %H:%M'))-28800)
    if event["TriggerName"] == "Week":
        now = int(time.mktime(time.strptime(
            startDate+" 07:03", '%Y-%m-%d %H:%M'))-28800)
    if event["TriggerName"] == "TwoDays":
        now = int(time.mktime(time.strptime(
            startDate+" 18:00", '%Y-%m-%d %H:%M'))-28800)
    if event["TriggerName"] == "Exam":
        now = int(time.mktime(time.strptime(
            startDate+" 07:05", '%Y-%m-%d %H:%M'))-28800)
    if event["TriggerName"] == "Exam_2":
        now = int(time.mktime(time.strptime(
            startDate+" 18:10", '%Y-%m-%d %H:%M'))-28800)
    return now


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

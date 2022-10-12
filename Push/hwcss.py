# -*- coding: utf8 -*-
import json
import time
import requests
from functools import cmp_to_key
import pymysql
import traceback
import sys
now = time.time()
startDate = time.strftime("%Y-%m-%d", time.localtime(now+28800))
num = ""
DB = pymysql.connect(host='localhost',
                     port=0000,
                     user='user',
                     password='password',
                     database='database')


def push(list, data, msg):
    list = sorted(list, key=cmp_to_key(
        cmp_deadline), reverse=True)
    title = data["title"]
    for i in list:
        courseName = i["courseName"]
        homeworkName = i["homeworkName"]
        data["title"] = "【" + title+"】"+courseName+"  "+homeworkName
        deadlineDate = i["deadlineDate"]
        data["message"] = msg+f"<br>课程名称：{courseName}<br>作业名称：{homeworkName}<br>截止时间：{deadlineDate}"+dayOfTheWeek(
            deadlineDate)
        requests.post(
            "https://example.tencentcs.com/release/push"+num+"/textcard", data=data)


def push_2(list, data, msg):
    list = sorted(list, key=cmp_to_key(
        cmp_deadline), reverse=True)
    title = data["title"]
    for i in list:
        courseName = i["courseName"]
        data["title"] = "【" + title+"】"+courseName+"  "+homeworkName
        homeworkName = i["homeworkName"]
        deadlineDate = i["deadlineDate"]
        data["message"] = msg + \
            f"<br>课程名称：{courseName}<br>作业名称：{homeworkName}<br>截止时间：{deadlineDate}"
        requests.post(
            "https://example.tencentcs.com/release/push"+num+"/textcard", data=data)


def filter(list, down, up):
    newList = []
    for i in list:
        dl = time.mktime(time.strptime(
            i["deadlineDate"], '%Y-%m-%d %H:%M'))-now-28800
        if dl >= down and dl <= up:
            newList.append(i)
    return newList


def HWCSS(wxID, Bind=False, Create=False, Morning=False, Night=False, Preview0=False, Week=False, ThreeDays=False, HomeworkSESSION=""):
    DB.ping(reconnect=True)
    cursor = DB.cursor()
    try:
        if not HomeworkSESSION:
            sql = "SELECT HomeworkSESSION FROM user WHERE WeChatName='%s'" % (
                wxID)
            DB.ping(reconnect=True)
            cursor.execute(sql)
            HomeworkSESSION = cursor.fetchone()[0]
        session = requests.session()
        session.get('https://hw.dgut.edu.cn/login')
        session.cookies.set("SESSION", HomeworkSESSION)
        HW = json.loads(session.get(
            'https://hw.dgut.edu.cn/api/student/plan?size=100&sort=deadline_date,desc').text)
        if HW["code"] != 0:
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
                "OB": "1",
                "QB": "0"
            }
            response = requests.post(
                f"https://example.tencentcs.com/release/checkCSS"+num, data=data)
            response = json.loads(response.text)
            if "HomeworkSESSION" not in response.keys():
                sql = "UPDATE user SET HomeworkSESSION='' WHERE WeChatName='%s'" % (
                    wxID)
                DB.ping(reconnect=True)
                cursor.execute(sql)
                DB.commit()
                cursor.close()
                data = {
                    "title": '获取信息失败',
                    "message": '无法获取您的网安作业管理系统信息，已为您暂停服务。<br><br>若您修改了所绑定账号的密码，请点击下方“绑定账号”菜单以更新密码。<br><br>若您并未修改所绑定账号的密码，请联系开发者解决。',
                    "url": 'https://hw.dgut.edu.cn/student/homeworkPlan',
                    "user": wxID,
                    "agentid": '1000004',
                }
                requests.post(
                    "https://example.tencentcs.com/release/push"+num+"/textcard", data=data)
                time.sleep(3)
                return {"success": 0}
            if "HomeworkSESSION" in response.keys() and response["HomeworkSESSION"] != "error":
                sql = "UPDATE user SET HomeworkSESSION='%s' WHERE WeChatName='%s'" % (
                    response["HomeworkSESSION"], wxID)
                DB.ping(reconnect=True)
                cursor.execute(sql)
                DB.commit()
                session.cookies.set("SESSION", response["HomeworkSESSION"])
                HW = json.loads(session.get(
                    'https://hw.dgut.edu.cn/api/student/plan?size=100&sort=deadline_date,desc').text)
                if HW["code"] != 0:
                    for i in range(3):
                        time.sleep(3)
                        HW = json.loads(session.get(
                            'https://hw.dgut.edu.cn/api/student/plan?size=100&sort=deadline_date,desc').text)
                        if HW["code"] == 0:
                            break
                if HW["code"] != 0:
                    traceback.print_exc()
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    error = str(repr(traceback.format_exception(
                        exc_type, exc_value, exc_traceback)))
                    e = {
                        "MSG": "hwcss,"+error,
                        "USER": 'Chang',
                        "AGENTID": '1000005',
                    }
                    requests.post(
                        "https://example.tencentcs.com/release/push"+num+"/text", data=e)
                    cursor.close()
                    time.sleep(3)
                    return {"success": 0}
            else:
                traceback.print_exc()
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error = str(repr(traceback.format_exception(
                    exc_type, exc_value, exc_traceback)))
                e = {
                    "MSG": "hwcss,"+error,
                    "USER": 'Chang',
                    "AGENTID": '1000005',
                }
                requests.post(
                    "https://example.tencentcs.com/release/push"+num+"/text", data=e)
                cursor.close()
                time.sleep(3)
                return {"success": 0}
    except:
        traceback.print_exc()
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error = str(repr(traceback.format_exception(
            exc_type, exc_value, exc_traceback)))
        e = {
            "MSG": "hwcss,"+error,
            "USER": 'Chang',
            "AGENTID": '1000005',
        }
        requests.post(
            "https://example.tencentcs.com/release/push"+num+"/text", data=e)
        cursor.close()
        time.sleep(3)
        return {"success": 0}

    cursor.close()
    HW = HW["data"]["data"]
    notSubmitted = []
    for i in HW:
        if i["submitted"] == False:
            if time.mktime(time.strptime(
                    i["deadlineDate"], '%Y-%m-%d %H:%M'))-now-28800 > 0:
                notSubmitted.append(i)
    data = {
        "url": 'https://hw.dgut.edu.cn/student/homeworkPlan',
        "user": wxID,
        "agentid": '1000004',
    }
    if Bind:
        data['title'] = '绑定成功'
        notSubmitted = sorted(notSubmitted, key=cmp_to_key(cmp_deadline))
        if notSubmitted:
            recently = notSubmitted[0]
            courseName = recently["courseName"]
            homeworkName = recently["homeworkName"]
            deadlineDate = recently["deadlineDate"]
            data["message"] = f"最近需要提交的作业：<br>课程名称：{courseName}<br>作业名称：{homeworkName}<br>截止时间：{deadlineDate}"+dayOfTheWeek(
                deadlineDate)
        else:
            data["message"] = "最近没有需要提交的作业。",
        requests.post(
            "https://example.tencentcs.com/release/push"+num+"/textcard", data=data)
    if Create:
        data['title'] = '新作业'
        newCreate = []
        for i in notSubmitted:
            new = now-time.mktime(time.strptime(
                i["createTime"], '%Y-%m-%d %H:%M'))+28800
            if new <= 10810:
                newCreate.append(i)
        push_2(newCreate, data, "老师发布了新作业：")
        data['title'] = '即将截止'
        quick = []
        quick = filter(notSubmitted, 0, 16210)
        if not quick:
            return {}
        push(quick, data, "作业马上截止了！")
    elif Morning:
        data['title'] = '今日截止'
        cutOff = []
        cutOff = filter(notSubmitted, 0, 39730)
        if not cutOff:
            return {}
        push(cutOff, data, "以下作业需要在今日18:00前提交：")
    elif Night:
        data['title'] = '今晚截止'
        cutOff = []
        cutOff = filter(notSubmitted, 12590, 59410)
        if not cutOff:
            return {}
        push(cutOff, data, "以下作业需要今日晚上或明日凌晨前提交：")
    elif Preview0:
        data['title'] = '明晚截止'
        cutOff = []
        cutOff = filter(notSubmitted, 93590, 118810)
        if not cutOff:
            return {}
        push(cutOff, data, "以下作业需要明日晚上或后天凌晨前提交：")
    elif Week:
        data['title'] = '本周计划'
        plan = []
        plan = filter(notSubmitted, 0, 604810)
        if not plan:
            return {}
        push(plan, data, "本周（下周一9:00前）需要提交的作业：")
    elif ThreeDays:
        data['title'] = '三天后截止'
        plan = []
        plan = filter(notSubmitted, 215990, 302410)
        if len(plan) < 3:
            return {}
        push(plan, data, "三天后需要提交的作业较多，请合理安排时间。")

    time.sleep(3)
    return {"success": 1}


def main_handler(event, context):
    if "Type" in event.keys():
        if event["Type"] == "Timer":
            DB.ping(reconnect=True)
            cursor = DB.cursor()
            sql = "SELECT WeChatName FROM user WHERE HomeworkSESSION <>''"
            DB.ping(reconnect=True)
            cursor.execute(sql)
            rows = cursor.fetchall()
            nowtime(event)
            for row in rows:
                if event["TriggerName"] == "Create":
                    HWCSS(row[0], Create=True)
                if event["TriggerName"] == "Morning":
                    HWCSS(row[0], Morning=True)
                if event["TriggerName"] == "Night":
                    HWCSS(row[0], Night=True)
                if event["TriggerName"] == "Preview0":
                    HWCSS(row[0], Preview0=True)
                if event["TriggerName"] == "Week":
                    HWCSS(row[0], Week=True)
                if event["TriggerName"] == "ThreeDays":
                    HWCSS(row[0], ThreeDays=True)
            cursor.close()
            DB.close()
    if "requestContext" not in event.keys():
        return {}
    if "queryStringParameters" not in event.keys():
        return {}
    if event["requestContext"]["path"] == "/hwcss"+num and event["requestContext"]["httpMethod"] == "POST":
        WXID = event["queryStringParameters"]["WXID"]
        HomeworkSESSION = event["queryStringParameters"]["HomeworkSESSION"]
        json = HWCSS(WXID, Bind=True, HomeworkSESSION=HomeworkSESSION)
        DB.close()
        return json


def nowtime(event):
    global now
    if event["TriggerName"] == "Create":
        now = int(now)
    if event["TriggerName"] == "ThreeDays":
        now = int(time.mktime(time.strptime(
            startDate+" 19:00", '%Y-%m-%d %H:%M'))-28800)
    if event["TriggerName"] == "Week":
        now = int(time.mktime(time.strptime(
            startDate+" 09:00", '%Y-%m-%d %H:%M'))-28800)
    if event["TriggerName"] == "Preview0":
        now = int(time.mktime(time.strptime(
            startDate+" 22:00", '%Y-%m-%d %H:%M'))-28800)
    if event["TriggerName"] == "Night":
        now = int(time.mktime(time.strptime(
            startDate+" 14:30", '%Y-%m-%d %H:%M'))-28800)
    if event["TriggerName"] == "Morning":
        now = int(time.mktime(time.strptime(
            startDate+" 06:58", '%Y-%m-%d %H:%M'))-28800)


def cmp_deadline(hw_1, hw_2):
    d_1 = time.mktime(time.strptime(
        hw_1["deadlineDate"], '%Y-%m-%d %H:%M'))
    d_2 = time.mktime(time.strptime(
        hw_2["deadlineDate"], '%Y-%m-%d %H:%M'))
    if d_1 > d_2:
        return 1
    elif d_1 < d_2:
        return -1
    else:
        c_1 = time.mktime(time.strptime(
            hw_1["createTime"], '%Y-%m-%d %H:%M'))
        c_2 = time.mktime(time.strptime(
            hw_2["createTime"], '%Y-%m-%d %H:%M'))
        if c_1 > c_2:
            return 1
        else:
            return -1


def dayOfTheWeek(deadlineDate):
    week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    stime = time.strptime(deadlineDate, '%Y-%m-%d %H:%M')
    dayOfTheWeek = " "+week_list[stime.tm_wday]
    if stime.tm_hour >= 0 and stime.tm_hour <= 6:
        dayOfTheWeek = " "+week_list[stime.tm_wday]+"凌晨" + "<br>注意！该作业需要在  " + \
            week_list[stime.tm_wday-1]+"晚上 或 " + \
            week_list[stime.tm_wday]+"凌晨 提交。"
    elif stime.tm_hour > 6 and stime.tm_hour <= 12:
        dayOfTheWeek = " "+week_list[stime.tm_wday]+"早上"
    elif stime.tm_hour > 12 and stime.tm_hour < 18:
        dayOfTheWeek = " "+week_list[stime.tm_wday]+"下午"
    elif stime.tm_hour >= 18 and stime.tm_hour <= 23:
        dayOfTheWeek = " "+week_list[stime.tm_wday]+"晚上"
    return dayOfTheWeek

# -*- coding: utf8 -*-
import json
import requests
import pymysql
CORPID = 'exampleCorpid'
agentid = {
    "ci": "1000003",
    "ul": "1000002",
    "css": "1000004",
}

DB = pymysql.connect(host='localhost',
                     port=0000,
                     user='user',
                     password='password',
                     database='database')


def wx_push_text(message, user, agentid):
    json_dict = {
        "touser": user,
        "msgtype": "text",
        "agentid": agentid,
        "text": {
            "content": message
        },
        "safe": 0,
        "enable_id_trans": 0,
        "enable_duplicate_check": 0,
        "duplicate_check_interval": 1800
    }
    json_str = json.dumps(json_dict)
    DB.ping(reconnect=True)
    cursor = DB.cursor()
    sql = "SELECT ACCESS_TOKEN FROM wx WHERE id='%s'" % (agentid)
    DB.ping(reconnect=True)
    cursor.execute(sql)
    access_token = cursor.fetchone()[0]
    response_send = requests.post(
        f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}", data=json_str)
    data = json.loads(response_send.text)
    if data['errcode'] == 40014 or data['errcode'] == 42001:
        sql = "SELECT SECRET FROM wx WHERE id='%s'" % (agentid)
        DB.ping(reconnect=True)
        cursor.execute(sql)
        secret = cursor.fetchone()[0]
        access_token = gettoken(CORPID, secret)
        sql = "UPDATE wx SET ACCESS_TOKEN='%s' WHERE id='%s'" % (
            access_token, agentid)
        DB.ping(reconnect=True)
        cursor.execute(sql)
        DB.commit()
        response_send = requests.post(
            f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}", data=json_str)
    cursor.close()
    return json.loads(response_send.text)['errmsg'] == 'ok'


def wx_push_textcard(title, message, url, user, agentid):
    json_dict = {
        "touser": user,
        "msgtype": "textcard",
        "agentid": agentid,
        "textcard": {
            "title": title,
            "description": message,
            "url": url,
        },
    }
    json_str = json.dumps(json_dict)
    DB.ping(reconnect=True)
    cursor = DB.cursor()
    sql = "SELECT ACCESS_TOKEN FROM wx WHERE id='%s'" % (agentid)
    DB.ping(reconnect=True)
    cursor.execute(sql)
    access_token = cursor.fetchone()[0]
    response_send = requests.post(
        f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}", data=json_str)
    data = json.loads(response_send.text)
    if data['errcode'] == 40014 or data['errcode'] == 42001:
        sql = "SELECT SECRET FROM wx WHERE id='%s'" % (agentid)
        DB.ping(reconnect=True)
        cursor.execute(sql)
        secret = cursor.fetchone()[0]
        access_token = gettoken(CORPID, secret)
        sql = "UPDATE wx SET ACCESS_TOKEN='%s' WHERE id='%s'" % (
            access_token, agentid)
        DB.ping(reconnect=True)
        cursor.execute(sql)
        DB.commit()
        response_send = requests.post(
            f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}", data=json_str)
    cursor.close()
    return json.loads(response_send.text)['errmsg'] == 'ok'


def gettoken(corpid, secret):
    response = requests.get(
        f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={secret}")
    ret = json.loads(response.text)['access_token']
    return ret


def main_handler(event, context):
    if "requestContext" not in event.keys():
        return {}
    if "queryStringParameters" not in event.keys():
        return {}
    if event["requestContext"]["path"] == "/push/text" and event["requestContext"]["httpMethod"] == "POST":
        MSG = event["queryStringParameters"]["MSG"]
        USER = event["queryStringParameters"]["USER"]
        AGENTID = event["queryStringParameters"]["AGENTID"]
        wx_push_text(MSG, USER, AGENTID)
    if event["requestContext"]["path"] == "/push/textcard" and event["requestContext"]["httpMethod"] == "POST":
        title = event["queryStringParameters"]["title"]
        message = event["queryStringParameters"]["message"]
        url = event["queryStringParameters"]["url"]
        user = event["queryStringParameters"]["user"]
        agentid = event["queryStringParameters"]["agentid"]
        wx_push_textcard(title, message, url, user, agentid)
    DB.close()
    return {}

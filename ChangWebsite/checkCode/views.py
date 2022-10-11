'''
Author: AChangAZha
Date: 2022-06-30 23:10:21
LastEditTime: 2022-10-09 19:41:27
LastEditors: AChangAZha
'''
from django.shortcuts import render

# Create your views here.
from bind import models as bind_models
from checkCode import models as checkCode_models
import json
import requests
from django.http import HttpResponse
from django.conf import settings


def getAppSecret(type):
    return checkCode_models.WX.objects.get(id=settings.AGENTID[type]).SECRET


def getAppAccessToken(type):
    return checkCode_models.WX.objects.get(id=settings.AGENTID[type]).ACCESS_TOKEN


def checkCode(request):
    ret = {}
    if request.method == 'POST':
        code = request.POST.get('code')
        type = request.POST.get('type')
        if not code or not type:
            return HttpResponse(json.dumps(ret))
        if type not in settings.AGENTID.keys():
            return HttpResponse(json.dumps(ret))
        try:
            data = getWxname(code, getAppAccessToken(type))
        except:
            return HttpResponse(json.dumps({"error": "DB"}))
        if data['errcode'] == 40014 or data['errcode'] == 42001:
            try:
                ACCESS_TOKEN = gettoken(settings.CORPID, getAppSecret(type))
            except:
                return HttpResponse(json.dumps({"error": "DB"}))
            data = getWxname(code, ACCESS_TOKEN)
        if 'UserId' in data:
            wxID = data['UserId']
            user = None
            try:
                user = bind_models.User.objects.get(NAME=wxID)
            except:
                user = bind_models.User()
                user.WeChatName = wxID
                try:
                    user.save()
                except:
                    return HttpResponse(json.dumps({"error": "DB"}))
            if type == 'ul':
                if user.UlearningAUTHORIZATION:
                    return HttpResponse(json.dumps({"hadBind": 1}))
                if user.UlearningID:
                    ret['ID'] = user.UlearningID
            elif type == 'css' and user.HomeworkSESSION:
                return HttpResponse(json.dumps({"hadBind": 1}))
            elif type == 'ci' and user.DakaBEARER:
                return HttpResponse(json.dumps({"hadBind": 1}))
            elif type == 'ulc' and not user.UlearningID:
                return HttpResponse(json.dumps({"noBind": 1}))
            elif type == 'cssc' and not user.HomeworkSESSION:
                return HttpResponse(json.dumps({"noBind": 1}))
            elif type == 'cic' and not user.DakaBEARER:
                return HttpResponse(json.dumps({"noBind": 1, 'wxID': wxID}))
            ret['wxID'] = wxID
            if type == 'css' or type == 'ci':
                if user.StudentNumber:
                    ret['ID'] = user.StudentNumber
                if user.StudentPassword:
                    if (type == 'css' and user.DakaBEARER) or (type == 'ci' and user.HomeworkSESSION):
                        ret['OK'] = 1
            if type == 'css' and user.DakaBEARER:
                ret['QB'] = 1
    return HttpResponse(json.dumps(ret))


def gettoken(corpid, secret):
    response = requests.get(
        f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={secret}")
    ret = json.loads(response.text)['access_token']
    app = checkCode_models.WX.objects.get(SECRET=secret)
    app.ACCESS_TOKEN = ret
    app.save()
    return ret


def getWxname(code, accessToken):
    if not accessToken:
        return {'errcode': 40014}
    response = requests.get(
        f"https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?access_token={accessToken}&code={code}")
    return json.loads(response.text)

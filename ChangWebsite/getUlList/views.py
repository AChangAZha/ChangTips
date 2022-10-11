'''
Author: AChangAZha
Date: 2022-08-30 13:27:36
LastEditTime: 2022-10-11 00:37:14
LastEditors: AChangAZha
'''
import imp
import json
import requests
from django.shortcuts import render
from django.shortcuts import redirect, render
from checkCode.views import getWxname, getAppAccessToken, gettoken, getAppSecret
from django.conf import settings

# Create your views here.


def getUlList(request):
    if request.method == 'GET':
        code = request.GET.get('code')
        if not code:
            return redirect("/index")
        data = getWxname(code, getAppAccessToken("ul"))
        if data['errcode'] == 40014 or data['errcode'] == 42001:
            ACCESS_TOKEN = gettoken(settings.CORPID, getAppSecret("ul"))
            data = getWxname(code, ACCESS_TOKEN)
        if 'UserId' in data:
            wxID = data['UserId']
        else:
            return redirect("/index")
        j = {
            "wxid": wxID,
        }
        rtx = requests.post(
            'https://example.tencentcs.com/release/getullist', data=j)
        if json.loads(rtx.text).get("error"):
            return redirect("https://open.weixin.qq.com/connect/oauth2/authorize?appid=exampleCorpid&redirect_uri=https%3A%2F%2Fchangwebsite.azurewebsites.net%2Fbind%3Ftype%3Dul&response_type=code&scope=snsapi_base&state=#wechat_redirect")
        list = json.loads(rtx.text).get("list")
        txt = "结果仅供参考，详情请见优学院官方网站。"
        if not list:
            txt = "最近没有需要完成的任务。"
        return render(request, "ulList.html", {"list": list, "txt": txt})


def loading(request):
    return render(request, "loading.html")

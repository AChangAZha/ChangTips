'''
Author: AChangAZha
Date: 2022-06-02 09:09:01
LastEditTime: 2022-10-11 08:13:28
LastEditors: AChangAZha
'''
import base64
import json
from django.http import HttpResponse
from django.shortcuts import redirect, render
from bind import models
import requests
from django.conf import settings

# Create your views here.


def bind(request):
    ctx = {}
    if request.method == 'POST':
        if request.POST:
            wxID = request.POST.get('wxID')
            PWD = request.POST.get('PWD')
            ONE = request.POST.get('ONE')
            if not wxID or not(PWD or ONE):
                return HttpResponse(json.dumps(ctx))
            OB = "0"
            if ONE:
                try:
                    user = models.User.objects.get(NAME=wxID)
                    if not user.StudentNumber or not user.StudentPassword:
                        return HttpResponse(json.dumps(ctx))
                    StudentNumber = user.StudentNumber
                    StudentPassword = user.StudentPassword
                    OB = "1"
                except:
                    return HttpResponse(json.dumps({"success": "0"}))
            if request.POST.get('ul'):
                ID = request.POST.get('ul')
                ID = ID.replace(' ', '')
                if not ID:
                    return HttpResponse(json.dumps(ctx))
                data = {
                    "ID": ID,
                    "PWD": PWD,
                    "WXID": wxID
                }
                response = requests.post(
                    f"https://example.tencentcs.com/release/checkUl", data=data)  # 部署在腾讯云函数服务的验证第三方账号模块，通过API网关触发
                UlearningAUTHORIZATION = json.loads(
                    response.text).get('UlearningAUTHORIZATION')
                UlearningID2 = json.loads(response.text).get('UlearningID2')
                if UlearningAUTHORIZATION and UlearningAUTHORIZATION != "error":
                    if changeU(wxID, ID, PWD, UlearningAUTHORIZATION, UlearningID2):
                        return HttpResponse(json.dumps({"success": "1"}))
                    else:
                        return HttpResponse(json.dumps({"success": "0"}))
            if (request.POST.get('ci') or ONE == "ci"):
                if OB == "1":
                    ID = StudentNumber
                    PWD = StudentPassword
                else:
                    ID = request.POST.get('ci')
                    ID = ID.replace(' ', '')
                    if not ID:
                        return HttpResponse(json.dumps(ctx))
                data = {
                    "ID": ID,
                    "PWD": PWD,
                    "OB": OB,
                    "WXID": wxID
                }
                response = requests.post(
                    f"https://example.tencentcs.com/release/checkCI", data=data)
                DakaBEARER = json.loads(response.text).get('DakaBEARER')
                if OB == "1":
                    PWD = ""
                if DakaBEARER and DakaBEARER != "error":
                    if changeS(wxID, ID, PWD, '', DakaBEARER):
                        return HttpResponse(json.dumps({"success": "1"}))
                    else:
                        return HttpResponse(json.dumps({"success": "0"}))
            elif (request.POST.get('css') or ONE == "css"):
                if OB == "1":
                    ID = StudentNumber
                    PWD = StudentPassword
                else:
                    ID = request.POST.get('css')
                    ID = ID.replace(' ', '')
                    if not ID:
                        return HttpResponse(json.dumps(ctx))
                QB = "0"
                if 'QB' in request.POST:
                    if request.POST.get('QB') == "true":
                        QB = "1"
                data = {
                    "ID": ID,
                    "PWD": PWD,
                    "WXID": wxID,
                    "QB": QB,
                    "OB": OB
                }
                response = requests.post(
                    f"https://example.tencentcs.com/release/checkCSS", data=data)
                HomeworkSESSION = json.loads(
                    response.text).get('HomeworkSESSION')
                DakaBEARER = json.loads(response.text).get('DakaBEARER')
                if OB == "1":
                    PWD = ""
                if HomeworkSESSION and HomeworkSESSION != "error":
                    if changeS(wxID, ID, PWD, HomeworkSESSION, DakaBEARER):
                        return HttpResponse(json.dumps({"success": "1"}))
                    else:
                        return HttpResponse(json.dumps({"success": "0"}))
        return HttpResponse(json.dumps(ctx))
    elif request.method == 'GET':
        code = request.GET.get('code')
        if not code:
            return redirect("/index")
        type = request.GET.get('type')
        if type != 'ul' and type != 'css' and type != 'ci':
            return redirect("/index")
        ctx = {
            'type': type,
        }
        ctx['hidden'] = 'hidden'
        if type == 'ci':
            ctx['introduce'] = '（本功能仅供莞工用户使用）绑定莞工（新版）中央认证账号以接收每日疫情打卡提醒'
            ctx['idText'] = '学号'
            ctx['pwdText'] = '中央认证密码'
            ctx['hidden'] = ''
            return render(request, "bind.html", ctx)
        elif type == 'css':
            ctx['introduce'] = '（本功能仅供莞工网安学院等用户使用）绑定莞工（新版）中央认证账号以接收网安学院作业提交提醒'
            ctx['idText'] = '学号'
            ctx['pwdText'] = '中央认证密码'
            return render(request, "bind.html", ctx)
        elif type == 'ul':
            ctx['introduce'] = '绑定优学院账号以接收优学院任务提醒'
            ctx['idText'] = '优学院账号'
            return render(request, "bind.html", ctx)


def changeS(wxID, StudentNumber, StudentPassword, HomeworkSESSION, DakaBEARER):
    user = None
    try:
        user = models.User.objects.get(NAME=wxID)
    except:
        user = models.User()
        user.WeChatName = wxID
    try:
        if StudentNumber:
            user.StudentNumber = StudentNumber
        if StudentPassword:
            user.StudentPassword = encrypt(StudentPassword)
        if HomeworkSESSION:
            user.HomeworkSESSION = HomeworkSESSION
        if DakaBEARER:
            user.DakaBEARER = DakaBEARER
        user.save()
        return True
    except:
        return False


def changeU(wxID, UlearningID, UlearningPassword, UlearningAUTHORIZATION, UlearningID2):
    user = None
    try:
        user = models.User.objects.get(NAME=wxID)
    except:
        user = models.User()
        user.WeChatName = wxID
    try:
        user.UlearningID = UlearningID
        user.UlearningPassword = encrypt(UlearningPassword)
        user.UlearningAUTHORIZATION = UlearningAUTHORIZATION
        user.UlearningID2 = UlearningID2
        user.save()
        return True
    except:
        return False


def encrypt(PWD):
    return "encryptedPWD"


def cancelBinding(request):
    ctx = {}
    if request.method == 'POST':
        type = request.POST.get('type')
        wxID = request.POST.get('wxID')
        if type != 'ulc' and type != 'cssc' and type != 'cic':
            return HttpResponse(json.dumps(ctx))
        user = None
        try:
            user = models.User.objects.get(NAME=wxID)
            if not user.StudentNumber and not user.StudentPassword and not user.UlearningID and not user.UlearningPassword:
                return HttpResponse(json.dumps(ctx))
        except:
            return HttpResponse(json.dumps({"success": "0"}))
        if type == 'ulc':
            user.UlearningID = ''
            user.UlearningPassword = ''
            user.UlearningAUTHORIZATION = ''
            user.UlearningID2 = ''
        elif type == 'cssc':
            user.HomeworkSESSION = ''
            if not user.DakaBEARER:
                user.StudentNumber = ''
                user.StudentPassword = ''
        elif type == 'cic':
            user.DakaBEARER = ''
            if not user.HomeworkSESSION:
                user.StudentNumber = ''
                user.StudentPassword = ''
        try:
            user.save()
        except:
            return HttpResponse(json.dumps({"success": "0"}))
        return HttpResponse(json.dumps({"success": "1"}))
    elif request.method == 'GET':
        code = request.GET.get('code')
        if not code:
            return redirect("/index")
        type = request.GET.get('type')
        if type != 'ulc' and type != 'cssc' and type != 'cic':
            return redirect("/index")
        if type == 'cic':
            ctx['type'] = "莞工疫情打卡提醒"
            return render(request, "cancelBinding.html", ctx)
        elif type == 'cssc':
            ctx['type'] = "莞工网安作业提醒"
            return render(request, "cancelBinding.html", ctx)
        elif type == 'ulc':
            ctx['type'] = "优学院任务提醒"
            return render(request, "cancelBinding.html", ctx)
        return redirect("/index")


def success(request):
    type = request.GET.get('type')
    if type == 'ul' or type == 'css' or type == 'ci':
        ctx = {
            "successTips": "绑定",
            "text": "您将接收本功能的推送"
        }
    elif type == 'ulc' or type == 'cssc' or type == 'cic':
        ctx = {
            "successTips": "取消绑定",
            "text": "您将不再接收本功能的推送"
        }
    if type == 'ci':
        return render(request, "CiSuccess.html", ctx)
    return render(request, "success.html", ctx)


def tips(request):
    ctx = {
        "titleTips": "绑定账号",
        "tips": "提示",
        "text": "您已绑定，无需重复绑定"
    }
    return render(request, "tips.html", ctx)


def ctips(request):
    ctx = {
        "titleTips": "取消绑定",
        "tips": "提示",
        "text": "您尚未绑定，无需取消绑定"
    }
    return render(request, "tips.html", ctx)


def error(request):
    return render(request, "error.html")

'''
Author: AChangAZha
Date: 2022-06-30 23:10:20
LastEditTime: 2022-10-11 00:11:07
LastEditors: AChangAZha
'''
import re
from django.shortcuts import HttpResponse
from WXBizMsgCrypt3 import WXBizMsgCrypt
import xml.etree.cElementTree as ET
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from urllib.parse import quote
from bs4 import BeautifulSoup
import re
import random
import traceback
import sys

sReceiveId = "exampleCorpid"

# Create your views here.
api = {
    "ci": WXBizMsgCrypt("XVubfMylWM4", "zD6YksjugsfJSMkoz7b4kKGbbmg1G6W7aWKHkXqIMRM", "exampleCorpid"),
    "css": WXBizMsgCrypt("TQiymU", "2dyKqaTo0NPPr21gJz2wT7penUdoOVVYedhYaboeJIX", "exampleCorpid"),
    "ul": WXBizMsgCrypt("FFF7st68Id", "QydrDOvuJZcRFy6Z8Llf4EqTtTK8RgWcxfT4IRL4NkC", "exampleCorpid"),
    "fb": WXBizMsgCrypt("yV3O7N", "dQWnCp3hDBLiOcDSvum5qPOy6b5vvVnIDS18eiGV7Nu", "exampleCorpid"),
    "robot": WXBizMsgCrypt("tdyzOmnhEXM22UNaIlyE089m7", "8SDnLaXioUzjHSTTCiAHDJNmYdng6n1kysUZnMnRPlp", "exampleCorpid"),
}
MSG = {
    "ci": "欢迎使用莞工疫情打卡提醒功能！你将在每天凌晨十二点收到打卡提醒。绑定（新版）中央认证账号后，系统还可以定时检测当日打卡状态，在完成打卡之前会一直提醒哦。\n\n在绑定之前，请知悉：\n①绑定账号需要提交账号密码（请使用新版中央认证登录的账号密码），密码信息将被加密存储至服务器，仅用于提供提醒服务；\n②本功能的数据来源于东莞理工学院疫情防控打卡管理系统；\n③提醒成功与否受众多因素的影响，请勿过度依赖本功能。\n\n<a href=\"https://open.weixin.qq.com/connect/oauth2/authorize?appid=exampleCorpid&redirect_uri=https%3A%2F%2Fchangwebsite.azurewebsites.net%2Fbind%3Ftype%3Dci&response_type=code&scope=snsapi_base&state=#wechat_redirect\">点我立即前往绑定账号</a>\n如果怕被打扰，还可以在<a href=\"https://open.weixin.qq.com/connect/oauth2/authorize?appid=exampleCorpid&redirect_uri=https%3A%2F%2Fchangwebsite.azurewebsites.net%2FciSettings&response_type=code&scope=snsapi_base&state=#wechat_redirect\">推送管理</a>页面将不需要的推送关闭哦。",
    "css": "欢迎使用莞工网安作业提醒功能！绑定（新版）中央认证账号后，即可接收作业提醒。\n\n在绑定之前，请知悉：\n①绑定账号需要提交账号密码（请使用新版中央认证登录的账号密码），密码信息将被加密存储至服务器，仅用于提供提醒服务；\n②本功能的数据来源于东莞理工学院网络空间安全学院作业管理系统；\n③绑定成功后，你将会收到老师发布的新作业提醒以及作业提交提醒；\n④提醒成功与否受众多因素的影响，请勿过度依赖本功能。\n\n<a href=\"https://open.weixin.qq.com/connect/oauth2/authorize?appid=exampleCorpid&redirect_uri=https%3A%2F%2Fchangwebsite.azurewebsites.net%2Fbind%3Ftype%3Dcss&response_type=code&scope=snsapi_base&state=#wechat_redirect\">点我立即前往绑定账号</a>",
    "ul": "欢迎使用优学院任务提醒功能！绑定优学院账号后，即可接收任务提醒。\n\n在绑定之前，请知悉：\n①本功能的数据来源于优学院；\n②绑定账号需要提交账号密码，密码信息将被加密存储至服务器，仅用于提供提醒服务；\n③绑定成功后，你将会收到老师发布的新作业、讨论等提醒以及任务截止提醒；\n④提醒成功与否受众多因素的影响，请勿过度依赖本功能。\n\n<a href=\"https://open.weixin.qq.com/connect/oauth2/authorize?appid=exampleCorpid&redirect_uri=https%3A%2F%2Fchangwebsite.azurewebsites.net%2Fbind%3Ftype%3Dul&response_type=code&scope=snsapi_base&state=#wechat_redirect\">点我立即前往绑定账号</a>\n还可以<a href=\"https://open.weixin.qq.com/connect/oauth2/authorize?appid=exampleCorpid&redirect_uri=https%3A%2F%2Fchangwebsite.azurewebsites.net%2FUlList&response_type=code&scope=snsapi_base&state=#wechat_redirect\">一键查看最近未完成的任务</a>，无需打开APP或网页。",
    "fb": "在使用过程中如果有任何的问题或建议，欢迎向开发者反馈，有机会获得奖励哦。\n联系方式：https://changwebsite.azurewebsites.net/feedback\n腾讯兔小巢：https://support.qq.com/product/439480",
}
# 请求头1(百度搜索)
HEADERS_1 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0 Win64 x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36")',
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.baidu.com",
    "Cookie": 'ISSW=1; ISSW=1; BIDUPSID=76625397A1996FEB9E3DABE625746D5D; PSTM=1650762678; BD_UPN=12314753; BDUSS=hEVFVETjBvUmo1dXFNNGNNM1lpNC0yNzNLb2twYUdVcm5aeEt-d2dFaS1NSXhpRVFBQUFBJCQAAAAAAAAAAAEAAADFHj0hemhhbmdoZWhhbjY1NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL6jZGK-o2RibU; BDUSS_BFESS=hEVFVETjBvUmo1dXFNNGNNM1lpNC0yNzNLb2twYUdVcm5aeEt-d2dFaS1NSXhpRVFBQUFBJCQAAAAAAAAAAAEAAADFHj0hemhhbmdoZWhhbjY1NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL6jZGK-o2RibU; BAIDUID=C15F025CDDC5006DA62458D44AD3DFD8:SL=0:NR=50:FG=1; H_PS_PSSID=36426_36462_36455_34812_36422_36167_36487_36075_36055_36419_26350_36469_36312; sug=3; sugstore=0; ORIGIN=2; bdime=0; BDSVRTM=0; H_PS_645EC=7aa14K5rM5J+/w+6u4zIfy3M/PRoJEW/WL74nd9vYGpbQy28eNKnn8Nvh9E; channel=baidusearch; baikeVisitId=0b03d09e-e04e-49f0-9f80-e8ea292039e6'
}
# 请求头2(天气查询)
HEADERS_2 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0 Win64 x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36")',
    'Referer': 'http://www.weather.com.cn/',
}
# 请求头3(百度百科)
HEADERS_3 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0 Win64 x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36")',
}


# 用于跳出多层循环
class getOutOfLoop(Exception):
    pass


# 从中国天气网爬取的数据,保存各个城市与其对应的查询ID
with open("staticfiles/receive/city.json", 'rb') as city:
    cityDict = json.load(city)


@csrf_exempt
def receive(request):
    msg_signature = request.GET.get('msg_signature')
    timestamp = request.GET.get('timestamp')
    nonce = request.GET.get('nonce')
    type = request.GET.get('type')
    if not msg_signature or not timestamp or not nonce or not type:
        return HttpResponse()
    if type not in api.keys():
        return HttpResponse()
    if request.method == 'GET':
        echo_str = request.GET.get('echostr')
        ret, sEchoStr = api.get(type).VerifyURL(
            msg_signature, timestamp, nonce, echo_str)
        if (ret != 0):
            return HttpResponse("failed")
        else:
            return HttpResponse(sEchoStr)
    elif request.method == 'POST':
        sReqData = request.body
        ret, sMsg = api.get(type).DecryptMsg(
            sReqData, msg_signature, timestamp, nonce)
        if (ret != 0):
            return HttpResponse("failed")
        else:
            xml_tree = ET.fromstring(sMsg)
            toUser = xml_tree.find("FromUserName").text
            event = xml_tree.find("Event")
            msgType = xml_tree.find("MsgType")
            if event is not None:
                if event.text == 'subscribe':
                    msg = MSG[type]
                    sRespData = f"<xml><ToUserName><![CDATA[{toUser}]]></ToUserName><FromUserName><![CDATA[exampleCorpid]]></FromUserName><CreateTime>{timestamp}</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[{msg}]]></Content></xml>"
                    ret, sEncryptMsg = api.get(type).EncryptMsg(
                        sRespData, nonce, timestamp)
                    if (ret != 0):
                        return HttpResponse("failed")
                    else:
                        return HttpResponse(sEncryptMsg)
                if event.text == 'enter_agent' and type == 'robot':
                    msg = "天气查询：发送“今天东莞的天气如何？”或“广州天河区天气”等即可获得实时天气和今日天气预报（支持查询县级行政区的天气，如广州市天河区天气）。\n\n百度百科查询：发送你想了解的东西，如发送“Python”或“PHP”等可获得来自百度百科的介绍。\n\n当然你也可以问我其他问题，例如“世界上最好的语言是不是Python？”，这些问题我会交给百度来解决。"
                    sRespData = f"<xml><ToUserName><![CDATA[{toUser}]]></ToUserName><FromUserName><![CDATA[exampleCorpid]]></FromUserName><CreateTime>{timestamp}</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[{msg}]]></Content></xml>"
                    ret, sEncryptMsg = api.get(type).EncryptMsg(
                        sRespData, nonce, timestamp)
                    if (ret != 0):
                        return HttpResponse("failed")
                    else:
                        return HttpResponse(sEncryptMsg)
                return HttpResponse()
            if msgType.text == 'text' or msgType.text == 'image' or msgType.text == 'video' or msgType.text == 'link':
                if type == 'robot' and msgType.text == 'text':
                    buf = None
                    rec = xml_tree.find("Content").text
                    # 若问题中含有"天气"关键字则查询天气
                    if rec.find('天气') != -1:
                        buf = weather(rec)
                    # 如果没有查询结果,则转至下一个查询
                    if not buf:
                        # 查询百度百科
                        buf = encyclopedia(rec)
                    if not buf:
                        # 百度搜索
                        buf = search(rec)
                    msg = buf
                    sRespData = f"<xml><ToUserName><![CDATA[{toUser}]]></ToUserName><FromUserName><![CDATA[exampleCorpid]]></FromUserName><CreateTime>{timestamp}</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[{msg}]]></Content></xml>"
                    ret, sEncryptMsg = api.get(type).EncryptMsg(
                        sRespData, nonce, timestamp)
                    if (ret != 0):
                        return HttpResponse("failed")
                    else:
                        return HttpResponse(sEncryptMsg)
                elif toUser != 'Chang':
                    lucky = "0"
                    lucky, s = Lucky()
                    if msgType.text == 'text':
                        Content = xml_tree.find("Content").text
                    elif msgType.text == 'image':
                        Content = xml_tree.find(
                            "PicUrl").text+" "+xml_tree.find("MediaId").text
                    elif msgType.text == 'link':
                        Content = xml_tree.find("Url").text
                    else:
                        Content = "video:"+xml_tree.find("MediaId").text
                    data = {
                        "AGENTID": 1000005,
                        "MSG": toUser+" "+s+"\n"+Content+"\n"+type+" "+xml_tree.find("MsgId").text+" "+xml_tree.find("CreateTime").text,
                        "USER": "Chang",
                    }
                    requests.post(
                        'https://example.tencentcs.com/release/push/text', data=data)
                    if lucky != "0":
                        msg = "恭喜获得幸运奖："+lucky+"元红包！\n请发送接收奖励的微信所绑定的手机号（仅用于奖品发放），并在微信开启“允许通过手机号向我转账”（<a href=\"https://kf.qq.com/touch/sappfaq/190903b6rQRv190903Rb2eEb.html?scene_id=kf6814&state=123&platform=15\">点我查看开启方式</a>）。\n中奖编号：" + \
                            xml_tree.find("MsgId").text
                        sRespData = f"<xml><ToUserName><![CDATA[{toUser}]]></ToUserName><FromUserName><![CDATA[exampleCorpid]]></FromUserName><CreateTime>{timestamp}</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[{msg}]]></Content></xml>"
                        ret, sEncryptMsg = api.get(type).EncryptMsg(
                            sRespData, nonce, timestamp)
                        if (ret != 0):
                            return HttpResponse("failed")
                        else:
                            return HttpResponse(sEncryptMsg)
                else:
                    try:
                        Content = xml_tree.find("Content").text
                        str = Content.split('@')
                        data = {
                            "AGENTID": 1000005,
                            "MSG": str[1],
                            "USER": str[0],
                        }
                        requests.post(
                            'https://example.tencentcs.com/release/push/text', data=data)
                    except:
                        pass
            return HttpResponse()

# 将百度搜索中的链接转换为真实链接


def Lucky():
    ran = random.random()
    if ran < 0.9:
        return "0", " "
    else:
        return "1", "中奖"


def get_real_url(v_url):
    r = requests.get(v_url, headers=HEADERS_1, allow_redirects=False)
    if r.status_code == 302:
        real_url = r.headers.get('Location')
    else:
        real_url = re.findall("URL='(.*?)'", r.text)[0]
    return real_url


# 查询百度百科
def encyclopedia(data):
    info = requests.get(
        'https://baike.baidu.com/item/'+data, headers=HEADERS_3)
    info.encoding = 'utf-8'
    soup = BeautifulSoup(info.text, 'html.parser')
    para = soup.find(class_='lemma-summary')
    # 没有查询结果则返回None
    if not para:
        return None
    # 查询成功则处理页面中的总结段落
    para = para.find_all(class_='para')
    str = ''
    for p in para:
        text = re.sub(
            '\[.*?\]', '', p.text).replace('\n', '').replace('\xa0', '')
        str = str+text+'\n'
    return str


# 百度搜索
def search(data):
    info = requests.get(
        'https://www.baidu.com/s?ie=UTF-8&wd='+data, headers=HEADERS_1)
    info.encoding = 'utf-8'
    soup = BeautifulSoup(info.text, 'html.parser')
    results = soup.find_all(class_='result c-container xpath-log new-pmd')
    i = 0
    str = ''
    for r in results:
        i += 1
        title = r.find(class_='c-title t t tts-title')
        str = str+title.text+'\n'
        str = str+r.find(class_='content-right_8Zs40').text+'\n'
        str = str+get_real_url(title.find('a')['href'])+'\n\n'
        # 仅提供5条搜索结果
        if i == 5:
            break
    str = str + '更多结果请点击：' + \
        'https://www.baidu.com/s?ie=UTF-8&wd='+quote(data)+'\n'
    return str


# 查询城市天气
def weather(data):
    id = '0'
    find = False
    try:
        # 从本地文件中查询城市对应ID
        for k_1, v_1 in cityDict.items():
            for k_2, v_2 in v_1.items():
                for k_3, v_3 in v_2.items():
                    if data.find(k_3) != -1:
                        id = v_3['AREAID']
                        find = True
                if find:
                    raise getOutOfLoop()
    except getOutOfLoop:
        pass
    # 查询失败则返回None
    if not find:
        return None
    info = requests.get(
        'http://d1.weather.com.cn/sk_2d/'+id+'.html', headers=HEADERS_2)
    info.encoding = 'utf-8'
    details = re.search(
        r'"cityname":"([\s\S]*?)",', info.text).group(1)+' '+re.search(
        r'"time":"([\s\S]*?)",', info.text).group(1)+'实况：'+re.search(
        r'"temp":"(\d+)",', info.text).group(1)+'℃ 天气：'+re.search(
        r'"weather":"([\s\S]*?)",', info.text).group(1)+'\n今日最低/最高气温：'
    info = requests.get(
        'http://d1.weather.com.cn/dingzhi/'+id+'.html', headers=HEADERS_2)
    info.encoding = 'utf-8'
    details = details+re.search(
        r'"tempn":"([\s\S]*?)",', info.text).group(1)+'/'+re.search(
        r'"temp":"([\s\S]*?)",', info.text).group(1)+' '+re.search(
        r'"weather":"([\s\S]*?)",', info.text).group(1)+'\n'
    return details

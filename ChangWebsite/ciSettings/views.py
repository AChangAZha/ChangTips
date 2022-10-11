'''
Author: AChangAZha
Date: 2022-08-28 13:57:13
LastEditTime: 2022-08-29 13:27:28
LastEditors: AChangAZha
'''
from django.shortcuts import redirect, render
from ciSettings import models as ciSettings_models
from django.http import HttpResponse
import json
# Create your views here.


def ciSettings(request):
    if request.method == 'GET':
        code = request.GET.get('code')
        if not code:
            return redirect("/index")
        return render(request, "settings.html")
    if request.method == 'POST':
        wxID = request.POST.get('wxID')
        zero = request.POST.get('zero')
        continued = request.POST.get('continued')
        user = None
        try:
            user = ciSettings_models.ci.objects.get(NAME=wxID)
        except:
            return HttpResponse(json.dumps({"error": 0}))
        try:
            if zero == "false":
                user.zero = "0"
            else:
                user.zero = "1"
            if continued == "false":
                user.continued = "0"
            else:
                user.continued = "1"
            user.save()
            return HttpResponse(json.dumps({"OK": 1}))
        except:
            return HttpResponse(json.dumps({"error": -1}))


def getCi(request):
    if request.method == 'POST':
        wxID = request.POST.get('wxID')
        user = None
        try:
            user = ciSettings_models.ci.objects.get(NAME=wxID)
        except:
            user = ciSettings_models.ci()
            user.NAME = wxID
            user.zero = "1"
            user.continued = "1"
            try:
                user.save()
                return HttpResponse(json.dumps({"OK": 1, "zero": "1", "continued": "1"}))
            except:
                return HttpResponse(json.dumps({"error": "DB"}))
        try:
            return HttpResponse(json.dumps({"OK": 1, "zero": user.zero, "continued": user.continued}))
        except:
            return HttpResponse(json.dumps({"error": -1}))

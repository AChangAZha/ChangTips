'''
Author: AChangAZha
Date: 2022-06-02 09:39:50
LastEditTime: 2022-10-07 10:05:13
LastEditors: AChangAZha
'''
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, "index.html")


def qa(request):
    return render(request, "qa.html")


def qrcode(request):
    return render(request, "qrcode.html")


def feedback(request):
    return render(request, "feedback.html")


def introduce(request):
    return render(request, "introduce.html")

'''
Author: AChangAZha
Date: 2022-06-02 09:01:32
LastEditTime: 2022-10-07 01:04:04
LastEditors: AChangAZha
'''
"""ChangWebsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from getUlList import views as getUlList_views
from django.conf import settings
from bind import views as bind_views
from index import views as index_views
from checkCode import views as checkCode_views
from receive import views as receive_views
from ciSettings import views as ciSettings_views
from django.urls import path
urlpatterns = [
    path('', index_views.index, name='index'),
    path('index', index_views.index),
    path('qrcode', index_views.qrcode),
    path('qa', index_views.qa),
    path('feedback', index_views.feedback),
    path('introduce', index_views.introduce),
    path('bind', bind_views.bind, name='bind'),
    path('checkCode', checkCode_views.checkCode, name='checkCode'),
    path('bind/cancel', bind_views.cancelBinding, name='cancelBinding'),
    path('bind/success', bind_views.success, name='bindSuccess'),
    path('bind/tips', bind_views.tips, name='bindTips'),
    path('bind/ctips', bind_views.ctips, name='bindCtips'),
    path('receive', receive_views.receive),
    path('error', bind_views.error),
    path('ciSettings', ciSettings_views.ciSettings),
    path('getCi', ciSettings_views.getCi),
    path('getUlList', getUlList_views.getUlList),
    path('UlList', getUlList_views.loading)
]

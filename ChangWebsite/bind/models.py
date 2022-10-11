'''
Author: AChangAZha
Date: 2022-06-02 09:09:01
LastEditTime: 2022-10-11 00:31:21
LastEditors: AChangAZha
'''

# Create your models here.


from django.db import models


class User(models.Model):

    StudentNumber = models.CharField(max_length=128, null=True)
    UlearningPassword = models.CharField(max_length=256, null=True)
    StudentPassword = models.CharField(max_length=256, null=True)
    UlearningID = models.CharField(max_length=128, null=True)
    HomeworkSESSION = models.CharField(max_length=256, null=True)
    DakaBEARER = models.CharField(max_length=256, null=True)
    UlearningAUTHORIZATION = models.CharField(max_length=256, null=True)
    WeChatName = models.CharField(max_length=128, unique=True)
    UlearningID2 = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.WeChatName

    class Meta:
        ordering = ["WeChatName"]

'''
Author: AChangAZha
Date: 2022-08-28 13:57:13
LastEditTime: 2022-08-28 14:27:22
LastEditors: AChangAZha
'''
from django.db import models

# Create your models here.


class ci(models.Model):
    zero = models.CharField(max_length=1, null=False)
    continued = models.CharField(max_length=1, null=False)
    NAME = models.CharField(max_length=128, unique=True)

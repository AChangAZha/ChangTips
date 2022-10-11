from django.db import models

# Create your models here.


class WX(models.Model):
    ACCESS_TOKEN = models.CharField(max_length=256)
    SECRET = models.CharField(max_length=256)

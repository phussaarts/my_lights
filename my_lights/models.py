from django.db import models


class HueAuth(models.Model):
    client_id = models.CharField(max_length=50, unique=True)
    client_secret = models.CharField(max_length=50, unique=True)
    access_token = models.CharField(max_length=50, unique=True)
    refresh_token = models.CharField(max_length=50, unique=True)
    app_id = models.CharField(max_length=50, unique=True)
    device_id = models.CharField(max_length=50, unique=True)


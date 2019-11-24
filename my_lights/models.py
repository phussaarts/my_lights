from django.db import models
from django.contrib.auth.models import User


class HueAuthBase(models.Model):
    client_id = models.CharField(max_length=50, unique=True)
    client_secret = models.CharField(max_length=50, unique=True)
    app_id = models.CharField(max_length=50, unique=True)


class HueAuth(models.Model):
    access_token = models.CharField(max_length=50, unique=True, null=True)
    refresh_token = models.CharField(max_length=50, unique=True, null=True)
    device_id = models.CharField(max_length=50, unique=True)
    identifier = models.CharField(max_length=50, unique=True, null=True)
    user_name_device = models.CharField(max_length=50, unique=True, null=True)

    # todo implement refresh token method

    def __str__(self):
        return self.device_id


class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_device = models.ForeignKey(HueAuth, related_name='device', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username




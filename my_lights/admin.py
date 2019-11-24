from django.contrib import admin
from .models import HueAuth, HueAuthBase, UserProfile

admin.site.register(HueAuth)
admin.site.register(HueAuthBase)
admin.site.register(UserProfile)

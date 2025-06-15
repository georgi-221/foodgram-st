from django.contrib import admin
from django.contrib.auth import get_user_model

from custom_user.models import Subscription

admin.site.register(Subscription)
admin.site.register(get_user_model())

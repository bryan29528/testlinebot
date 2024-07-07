from django.contrib import admin
from botapp.models import users

class usersAdmin(admin.ModelAdmin):
    list_display=('uid','question','asktime','resSF','restext')
admin.site.register(users, usersAdmin)
from django.contrib import admin
from .models import *


# Register your models here.
class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'full_name', 'telegram_id', 'time_create')
    list_display_links = ('id', 'user_name')
    search_fields = ('user_name', 'full_name', 'telegram_id')


class UsersRequestsAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'response', 'time_create')
    # list_display_links = ('user_id', 'response')


admin.site.register(Users, UsersAdmin)
admin.site.register(UsersRequests, UsersRequestsAdmin)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserData

class UserDataInline(admin.StackedInline):
    model = UserData
    extra = 0
    fields = ('sex', 'age')

@admin.register(UserData)
class UserDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'sex', 'age')
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user',)
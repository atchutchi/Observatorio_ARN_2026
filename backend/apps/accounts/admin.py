from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'operator', 'is_active']
    list_filter = ['role', 'is_active', 'operator']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Observatório', {'fields': ('role', 'operator', 'phone', 'position')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Observatório', {'fields': ('role', 'operator', 'phone', 'position')}),
    )

from django.contrib import admin
from .models import OperatorType, Operator


@admin.register(OperatorType)
class OperatorTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'operator_type', 'is_active']
    list_filter = ['operator_type', 'is_active']
    search_fields = ['name', 'code', 'legal_name']

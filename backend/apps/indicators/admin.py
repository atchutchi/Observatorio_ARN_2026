from django.contrib import admin
from .models import IndicatorCategory, Indicator, OperatorTypeIndicator, Period


@admin.register(IndicatorCategory)
class IndicatorCategoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'code', 'name', 'is_cumulative']
    ordering = ['order']


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'unit', 'level', 'is_calculated']
    list_filter = ['category', 'unit', 'level', 'is_calculated']
    search_fields = ['code', 'name']
    ordering = ['category__order', 'order']


@admin.register(OperatorTypeIndicator)
class OperatorTypeIndicatorAdmin(admin.ModelAdmin):
    list_display = ['operator_type', 'indicator', 'is_applicable', 'is_mandatory']
    list_filter = ['operator_type', 'is_applicable', 'is_mandatory']


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ['year', 'quarter', 'month', 'is_locked']
    list_filter = ['year', 'quarter', 'is_locked']
    ordering = ['-year', '-month']

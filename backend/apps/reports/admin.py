from django.contrib import admin
from .models import Report, ReportTemplate


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'year', 'quarter', 'status', 'generated_at']
    list_filter = ['report_type', 'status', 'year']
    search_fields = ['title']


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'is_default']
    list_filter = ['report_type', 'is_default']

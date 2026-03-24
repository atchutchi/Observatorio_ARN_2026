from django.contrib import admin
from .models import DataEntry, CumulativeData, FileUpload, DataValidationRule


@admin.register(DataEntry)
class DataEntryAdmin(admin.ModelAdmin):
    list_display = ['indicator', 'operator', 'period', 'value', 'source', 'is_validated']
    list_filter = ['operator', 'source', 'is_validated', 'period__year', 'period__quarter']
    search_fields = ['indicator__code', 'indicator__name']
    raw_id_fields = ['indicator', 'period']


@admin.register(CumulativeData)
class CumulativeDataAdmin(admin.ModelAdmin):
    list_display = ['indicator', 'operator', 'year', 'cumulative_type', 'value', 'is_validated']
    list_filter = ['operator', 'year', 'cumulative_type', 'is_validated']


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'operator', 'file_type', 'year', 'status', 'uploaded_at']
    list_filter = ['operator', 'file_type', 'status', 'year']


@admin.register(DataValidationRule)
class DataValidationRuleAdmin(admin.ModelAdmin):
    list_display = ['indicator', 'rule_type', 'value', 'error_message']
    list_filter = ['rule_type']

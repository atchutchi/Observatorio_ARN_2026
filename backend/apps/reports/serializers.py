from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(
        source='generated_by.get_full_name', read_only=True, default='',
    )
    pdf_url = serializers.FileField(source='pdf_file', read_only=True)
    excel_url = serializers.FileField(source='excel_file', read_only=True)
    docx_url = serializers.FileField(source='docx_file', read_only=True)

    class Meta:
        model = Report
        fields = [
            'id', 'title', 'report_type', 'year', 'quarter', 'status',
            'generated_at', 'generated_by_name', 'executive_summary',
            'pdf_url', 'excel_url', 'docx_url', 'error_log',
        ]
        read_only_fields = ['id', 'generated_at', 'status', 'pdf_url', 'excel_url', 'docx_url']


class ReportGenerateSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=['quarterly', 'annual', 'custom'])
    year = serializers.IntegerField()
    quarter = serializers.IntegerField(required=False, allow_null=True)
    title = serializers.CharField(required=False, max_length=300)
    sections = serializers.DictField(required=False)

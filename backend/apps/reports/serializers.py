from rest_framework import serializers
from apps.operators.models import Operator
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(
        source='generated_by.get_full_name', read_only=True, default='',
    )
    pdf_url = serializers.FileField(source='pdf_file', read_only=True)
    excel_url = serializers.FileField(source='excel_file', read_only=True)
    docx_url = serializers.FileField(source='docx_file', read_only=True)
    operator_name = serializers.CharField(source='operator.name', read_only=True)
    operator_code = serializers.CharField(source='operator.code', read_only=True)

    class Meta:
        model = Report
        fields = [
            'id', 'title', 'report_type', 'year', 'quarter', 'status',
            'operator_scope', 'operator', 'operator_name', 'operator_code',
            'generated_at', 'generated_by_name', 'executive_summary',
            'pdf_url', 'excel_url', 'docx_url', 'error_log',
        ]
        read_only_fields = [
            'id', 'generated_at', 'status', 'pdf_url', 'excel_url', 'docx_url',
            'operator_name', 'operator_code',
        ]


class ReportGenerateSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=['quarterly', 'annual', 'custom'])
    year = serializers.IntegerField()
    quarter = serializers.IntegerField(required=False, allow_null=True)
    title = serializers.CharField(required=False, max_length=300)
    operator_scope = serializers.ChoiceField(
        choices=['all', 'operator', 'others'], required=False, default='all',
    )
    operator = serializers.PrimaryKeyRelatedField(
        queryset=Operator.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    operator_code = serializers.CharField(required=False, allow_blank=True, write_only=True)
    sections = serializers.DictField(required=False)

    def validate(self, attrs):
        scope = attrs.get('operator_scope') or 'all'
        operator_code = attrs.pop('operator_code', '').strip().upper()

        if operator_code and scope == 'operator' and not attrs.get('operator'):
            try:
                attrs['operator'] = Operator.objects.get(code=operator_code, is_active=True)
            except Operator.DoesNotExist as exc:
                raise serializers.ValidationError({
                    'operator_code': 'Operador seleccionado não existe ou não está activo.',
                }) from exc

        if scope == 'operator' and not attrs.get('operator'):
            raise serializers.ValidationError({
                'operator': 'Seleccione uma operadora para gerar relatório isolado.',
            })

        if scope != 'operator':
            attrs['operator'] = None

        return attrs

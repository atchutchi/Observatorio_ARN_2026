from rest_framework import serializers
from .models import DataEntry, CumulativeData, FileUpload


class DataEntrySerializer(serializers.ModelSerializer):
    indicator_code = serializers.CharField(source='indicator.code', read_only=True)
    indicator_name = serializers.CharField(source='indicator.name', read_only=True)
    operator_code = serializers.CharField(source='operator.code', read_only=True)
    period_display = serializers.CharField(source='period.__str__', read_only=True)

    class Meta:
        model = DataEntry
        fields = [
            'id', 'indicator', 'indicator_code', 'indicator_name',
            'operator', 'operator_code', 'period', 'period_display',
            'value', 'observation', 'source', 'is_validated',
            'submitted_by', 'submitted_at', 'updated_at',
            'validated_by', 'validated_at',
        ]
        read_only_fields = ['id', 'submitted_by', 'submitted_at', 'updated_at', 'validated_by', 'validated_at']


class DataEntryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataEntry
        fields = ['indicator', 'operator', 'period', 'value', 'observation']

    def validate(self, attrs):
        from apps.indicators.models import OperatorTypeIndicator
        operator = attrs['operator']
        indicator = attrs['indicator']

        applicable = OperatorTypeIndicator.objects.filter(
            operator_type=operator.operator_type,
            indicator=indicator,
            is_applicable=True,
        ).exists()
        if not applicable:
            raise serializers.ValidationError(
                f"Indicador '{indicator.name}' não é aplicável a {operator.name}"
            )
        return attrs


class BulkDataEntrySerializer(serializers.Serializer):
    """Aceita múltiplas entradas de dados de uma vez"""
    entries = DataEntryCreateSerializer(many=True)

    def create(self, validated_data):
        user = self.context['request'].user
        entries = []
        for entry_data in validated_data['entries']:
            obj, _ = DataEntry.objects.update_or_create(
                indicator=entry_data['indicator'],
                operator=entry_data['operator'],
                period=entry_data['period'],
                defaults={
                    'value': entry_data['value'],
                    'observation': entry_data.get('observation', ''),
                    'submitted_by': user,
                    'source': 'manual',
                    'is_validated': False,
                },
            )
            entries.append(obj)
        return entries


class CumulativeDataSerializer(serializers.ModelSerializer):
    indicator_code = serializers.CharField(source='indicator.code', read_only=True)
    indicator_name = serializers.CharField(source='indicator.name', read_only=True)
    operator_code = serializers.CharField(source='operator.code', read_only=True)

    class Meta:
        model = CumulativeData
        fields = [
            'id', 'indicator', 'indicator_code', 'indicator_name',
            'operator', 'operator_code', 'year', 'cumulative_type',
            'value', 'observation', 'source', 'is_validated',
            'submitted_by', 'submitted_at', 'updated_at',
        ]
        read_only_fields = ['id', 'submitted_by', 'submitted_at', 'updated_at']


class CumulativeDataCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CumulativeData
        fields = ['indicator', 'operator', 'year', 'cumulative_type', 'value', 'observation']

    def validate(self, attrs):
        from apps.indicators.models import OperatorTypeIndicator
        operator = attrs['operator']
        indicator = attrs['indicator']

        applicable = OperatorTypeIndicator.objects.filter(
            operator_type=operator.operator_type,
            indicator=indicator,
            is_applicable=True,
        ).exists()
        if not applicable:
            raise serializers.ValidationError(
                f"Indicador '{indicator.name}' não é aplicável a {operator.name}"
            )
        return attrs


class BulkCumulativeDataSerializer(serializers.Serializer):
    entries = CumulativeDataCreateSerializer(many=True)

    def create(self, validated_data):
        user = self.context['request'].user
        entries = []
        for entry_data in validated_data['entries']:
            obj, _ = CumulativeData.objects.update_or_create(
                indicator=entry_data['indicator'],
                operator=entry_data['operator'],
                year=entry_data['year'],
                cumulative_type=entry_data['cumulative_type'],
                defaults={
                    'value': entry_data['value'],
                    'observation': entry_data.get('observation', ''),
                    'submitted_by': user,
                    'source': 'manual',
                    'is_validated': False,
                },
            )
            entries.append(obj)
        return entries


class FileUploadSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.name', read_only=True)

    class Meta:
        model = FileUpload
        fields = [
            'id', 'operator', 'operator_name', 'file', 'original_filename',
            'file_type', 'year', 'quarter', 'status',
            'processing_log', 'records_imported', 'records_errors',
            'uploaded_at', 'processed_at',
        ]
        read_only_fields = [
            'id', 'status', 'processing_log', 'records_imported',
            'records_errors', 'uploaded_at', 'processed_at',
        ]


class FileUploadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['file', 'file_type', 'year', 'quarter']


class ValidationActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    comment = serializers.CharField(required=False, allow_blank=True)

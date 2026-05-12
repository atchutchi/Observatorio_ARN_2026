from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.operators.models import Operator
from .models import DataEntry, CumulativeData, FileUpload, ReceivedDocument

User = get_user_model()


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
    received_document_filename = serializers.CharField(
        source='received_document.original_filename',
        read_only=True,
    )

    class Meta:
        model = FileUpload
        fields = [
            'id', 'operator', 'operator_name', 'file', 'original_filename',
            'file_type', 'year', 'quarter', 'status',
            'processing_log', 'records_imported', 'records_errors',
            'uploaded_at', 'processed_at', 'received_document',
            'received_document_filename',
        ]
        read_only_fields = [
            'id', 'status', 'processing_log', 'records_imported',
            'records_errors', 'uploaded_at', 'processed_at',
            'received_document', 'received_document_filename',
        ]


class FileUploadCreateSerializer(serializers.ModelSerializer):
    operator = serializers.PrimaryKeyRelatedField(
        queryset=Operator.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = FileUpload
        fields = ['file', 'file_type', 'year', 'quarter', 'operator']

    def validate(self, attrs):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and user.is_arn_staff and not attrs.get('operator'):
            raise serializers.ValidationError({
                'operator': 'Seleccione o operador associado ao ficheiro.',
            })
        return attrs


class ReceivedDocumentSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.name', read_only=True)
    operator_code = serializers.CharField(source='operator.code', read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    received_by_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    latest_import = serializers.SerializerMethodField()

    class Meta:
        model = ReceivedDocument
        fields = [
            'id', 'operator', 'operator_name', 'operator_code',
            'file', 'original_filename', 'document_type', 'document_type_display',
            'year', 'quarter', 'status', 'status_display',
            'priority', 'priority_display', 'assigned_to', 'assigned_to_name',
            'received_by', 'received_by_name', 'due_date', 'notes', 'checklist',
            'latest_import', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'original_filename', 'received_by', 'received_by_name',
            'created_at', 'updated_at',
        ]

    def get_assigned_to_name(self, obj):
        if not obj.assigned_to:
            return None
        return obj.assigned_to.get_full_name() or obj.assigned_to.username

    def get_received_by_name(self, obj):
        if not obj.received_by:
            return None
        return obj.received_by.get_full_name() or obj.received_by.username

    def get_latest_import(self, obj):
        upload = obj.imports.order_by('-uploaded_at').first()
        if not upload:
            return None
        return {
            'id': upload.id,
            'file_type': upload.file_type,
            'status': upload.status,
            'processing_log': upload.processing_log,
            'records_imported': upload.records_imported,
            'records_errors': upload.records_errors,
            'uploaded_at': upload.uploaded_at,
            'processed_at': upload.processed_at,
        }


class ReceivedDocumentCreateSerializer(serializers.ModelSerializer):
    operator = serializers.PrimaryKeyRelatedField(queryset=Operator.objects.filter(is_active=True))
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role__in=['admin_arn', 'analyst_arn']),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ReceivedDocument
        fields = [
            'operator', 'file', 'document_type', 'year', 'quarter', 'status',
            'priority', 'assigned_to', 'due_date', 'notes', 'checklist',
        ]


class ValidationActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    comment = serializers.CharField(required=False, allow_blank=True)

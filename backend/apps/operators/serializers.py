from rest_framework import serializers
from .models import OperatorType, Operator


class OperatorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperatorType
        fields = ['id', 'code', 'name', 'description']


class OperatorSerializer(serializers.ModelSerializer):
    operator_type_name = serializers.CharField(source='operator_type.name', read_only=True)
    operator_type_code = serializers.CharField(source='operator_type.code', read_only=True)

    class Meta:
        model = Operator
        fields = [
            'id', 'name', 'legal_name', 'code', 'operator_type',
            'operator_type_name', 'operator_type_code',
            'license_number', 'contact_email', 'contact_phone',
            'director_name', 'address', 'logo', 'brand_color',
            'is_active', 'historical_names', 'created_at',
        ]


class OperatorListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for dropdowns and lists"""
    operator_type_code = serializers.CharField(source='operator_type.code', read_only=True)

    class Meta:
        model = Operator
        fields = ['id', 'name', 'code', 'operator_type_code', 'brand_color', 'is_active']

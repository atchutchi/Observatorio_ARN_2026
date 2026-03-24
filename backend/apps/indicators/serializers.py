from rest_framework import serializers
from .models import IndicatorCategory, Indicator, OperatorTypeIndicator, Period


class IndicatorChildSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Indicator
        fields = [
            'id', 'code', 'name', 'unit', 'level',
            'is_calculated', 'formula_type', 'order', 'notes', 'children',
        ]

    def get_children(self, obj):
        children = obj.children.all().order_by('order')
        return IndicatorChildSerializer(children, many=True).data


class IndicatorSerializer(serializers.ModelSerializer):
    category_code = serializers.CharField(source='category.code', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Indicator
        fields = [
            'id', 'code', 'name', 'category', 'category_code', 'category_name',
            'parent', 'unit', 'level', 'is_calculated', 'formula_type',
            'order', 'notes', 'children',
        ]

    def get_children(self, obj):
        children = obj.children.all().order_by('order')
        return IndicatorChildSerializer(children, many=True).data


class IndicatorFlatSerializer(serializers.ModelSerializer):
    """Flat serializer without children recursion, for bulk operations"""
    category_code = serializers.CharField(source='category.code', read_only=True)

    class Meta:
        model = Indicator
        fields = [
            'id', 'code', 'name', 'category', 'category_code',
            'parent', 'unit', 'level', 'is_calculated', 'formula_type', 'order',
        ]


class IndicatorCategorySerializer(serializers.ModelSerializer):
    indicators = serializers.SerializerMethodField()

    class Meta:
        model = IndicatorCategory
        fields = ['id', 'code', 'name', 'description', 'order', 'is_cumulative', 'indicators']

    def get_indicators(self, obj):
        root_indicators = obj.indicators.filter(parent__isnull=True).order_by('order')
        return IndicatorSerializer(root_indicators, many=True).data


class IndicatorCategoryListSerializer(serializers.ModelSerializer):
    indicator_count = serializers.IntegerField(source='indicators.count', read_only=True)

    class Meta:
        model = IndicatorCategory
        fields = ['id', 'code', 'name', 'order', 'is_cumulative', 'indicator_count']


class OperatorTypeIndicatorSerializer(serializers.ModelSerializer):
    indicator_code = serializers.CharField(source='indicator.code', read_only=True)
    indicator_name = serializers.CharField(source='indicator.name', read_only=True)
    indicator_unit = serializers.CharField(source='indicator.unit', read_only=True)
    indicator_level = serializers.IntegerField(source='indicator.level', read_only=True)
    category_code = serializers.CharField(source='indicator.category.code', read_only=True)
    category_name = serializers.CharField(source='indicator.category.name', read_only=True)

    class Meta:
        model = OperatorTypeIndicator
        fields = [
            'id', 'operator_type', 'indicator', 'indicator_code',
            'indicator_name', 'indicator_unit', 'indicator_level',
            'category_code', 'category_name',
            'is_applicable', 'is_mandatory', 'notes',
        ]


class PeriodSerializer(serializers.ModelSerializer):
    month_name = serializers.CharField(source='get_month_display', read_only=True)
    quarter_name = serializers.CharField(source='get_quarter_display', read_only=True)

    class Meta:
        model = Period
        fields = [
            'id', 'year', 'quarter', 'quarter_name', 'month', 'month_name',
            'start_date', 'end_date', 'is_locked',
        ]

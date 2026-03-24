from rest_framework import serializers


class SummarySerializer(serializers.Serializer):
    total_subscribers = serializers.FloatField()
    total_revenue = serializers.FloatField()
    total_data_traffic = serializers.FloatField()
    penetration_rate = serializers.FloatField()
    subscriber_change = serializers.FloatField()
    active_operators = serializers.IntegerField()
    year = serializers.IntegerField()
    quarter = serializers.IntegerField(allow_null=True)


class IndicatorDataSerializer(serializers.Serializer):
    indicator_code = serializers.CharField()
    indicator_name = serializers.CharField()
    indicator_level = serializers.IntegerField()
    operator_code = serializers.CharField()
    operator_name = serializers.CharField()
    operator_color = serializers.CharField()
    period = serializers.CharField()
    value = serializers.FloatField(allow_null=True)
    unit = serializers.CharField()


class MarketShareSerializer(serializers.Serializer):
    operator_code = serializers.CharField()
    operator_name = serializers.CharField()
    operator_color = serializers.CharField()
    value = serializers.FloatField()
    share_pct = serializers.FloatField()


class TrendSerializer(serializers.Serializer):
    period = serializers.CharField()
    total = serializers.FloatField(required=False)


class GrowthSerializer(serializers.Serializer):
    operator_code = serializers.CharField()
    operator_name = serializers.CharField()
    operator_color = serializers.CharField()
    current_value = serializers.FloatField()
    previous_value = serializers.FloatField()
    absolute_change = serializers.FloatField()
    pct_change = serializers.FloatField()


class HHISerializer(serializers.Serializer):
    hhi = serializers.FloatField()
    classification = serializers.CharField()
    operators = MarketShareSerializer(many=True)

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import OperatorType, Operator
from .serializers import OperatorTypeSerializer, OperatorSerializer, OperatorListSerializer


class OperatorTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OperatorType.objects.all()
    serializer_class = OperatorTypeSerializer
    permission_classes = [IsAuthenticated]


class OperatorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Operator.objects.select_related('operator_type').filter(is_active=True)
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return OperatorListSerializer
        return OperatorSerializer

    @action(detail=True, methods=['get'])
    def applicable_indicators(self, request, pk=None):
        operator = self.get_object()
        from apps.indicators.models import OperatorTypeIndicator
        from apps.indicators.serializers import OperatorTypeIndicatorSerializer

        mappings = (
            OperatorTypeIndicator.objects
            .filter(operator_type=operator.operator_type, is_applicable=True)
            .select_related('indicator', 'indicator__category')
            .order_by('indicator__category__order', 'indicator__order')
        )
        serializer = OperatorTypeIndicatorSerializer(mappings, many=True)
        return Response(serializer.data)

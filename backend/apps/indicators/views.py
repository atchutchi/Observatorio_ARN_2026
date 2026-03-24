from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import IndicatorCategory, Indicator, Period
from .serializers import (
    IndicatorCategorySerializer, IndicatorCategoryListSerializer,
    IndicatorFlatSerializer, PeriodSerializer,
)


class IndicatorCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IndicatorCategory.objects.prefetch_related('indicators').all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'code'

    def get_serializer_class(self):
        if self.action == 'list':
            return IndicatorCategoryListSerializer
        return IndicatorCategorySerializer


class IndicatorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Indicator.objects.select_related('category', 'parent').all()
    serializer_class = IndicatorFlatSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category__code', 'level', 'parent']


class PeriodViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['year', 'quarter', 'is_locked']

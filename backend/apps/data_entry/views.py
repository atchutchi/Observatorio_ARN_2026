from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.permissions import IsARNStaff, IsOwnerOrARN
from .models import DataEntry, CumulativeData, FileUpload
from .serializers import (
    DataEntrySerializer, BulkDataEntrySerializer,
    CumulativeDataSerializer, BulkCumulativeDataSerializer,
    FileUploadSerializer, FileUploadCreateSerializer,
    ValidationActionSerializer,
)


class DataEntryViewSet(viewsets.ModelViewSet):
    serializer_class = DataEntrySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'operator__code': ['exact'],
        'indicator__category__code': ['exact'],
        'indicator__code': ['exact'],
        'period__year': ['exact'],
        'period__quarter': ['exact'],
        'period__month': ['exact'],
        'is_validated': ['exact'],
        'source': ['exact'],
    }

    def get_queryset(self):
        qs = DataEntry.objects.select_related(
            'indicator', 'indicator__category', 'operator', 'period',
        ).order_by('indicator__category__order', 'indicator__order', 'period')

        user = self.request.user
        if user.is_operator_user and user.operator:
            qs = qs.filter(operator=user.operator)
        return qs

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = BulkDataEntrySerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        entries = serializer.save()
        return Response(
            DataEntrySerializer(entries, many=True).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'], permission_classes=[IsARNStaff])
    def validate_entry(self, request, pk=None):
        entry = self.get_object()
        ser = ValidationActionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        if ser.validated_data['action'] == 'approve':
            entry.is_validated = True
            entry.validated_by = request.user
            entry.validated_at = timezone.now()
            entry.save()
            return Response({'status': 'approved'})
        else:
            entry.is_validated = False
            comment = ser.validated_data.get('comment', '')
            if comment:
                entry.observation = f"[REJEITADO] {comment}"
            entry.save()
            return Response({'status': 'rejected'})

    @action(detail=False, methods=['get'], permission_classes=[IsARNStaff])
    def pending_validation(self, request):
        qs = self.get_queryset().filter(is_validated=False, source__in=['manual', 'upload'])
        page = self.paginate_queryset(qs)
        serializer = DataEntrySerializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


class CumulativeDataViewSet(viewsets.ModelViewSet):
    serializer_class = CumulativeDataSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'operator__code': ['exact'],
        'indicator__category__code': ['exact'],
        'year': ['exact'],
        'cumulative_type': ['exact'],
        'is_validated': ['exact'],
    }

    def get_queryset(self):
        qs = CumulativeData.objects.select_related(
            'indicator', 'indicator__category', 'operator',
        ).order_by('indicator__category__order', 'indicator__order', 'year', 'cumulative_type')

        user = self.request.user
        if user.is_operator_user and user.operator:
            qs = qs.filter(operator=user.operator)
        return qs

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = BulkCumulativeDataSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        entries = serializer.save()
        return Response(
            CumulativeDataSerializer(entries, many=True).data,
            status=status.HTTP_201_CREATED,
        )


class FileUploadViewSet(viewsets.ModelViewSet):
    serializer_class = FileUploadSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['operator__code', 'file_type', 'year', 'status']

    def get_queryset(self):
        qs = FileUpload.objects.select_related('operator').all()
        user = self.request.user
        if user.is_operator_user and user.operator:
            qs = qs.filter(operator=user.operator)
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return FileUploadCreateSerializer
        return FileUploadSerializer

    def perform_create(self, serializer):
        user = self.request.user
        operator = user.operator
        upload = serializer.save(
            operator=operator,
            uploaded_by=user,
            original_filename=self.request.FILES['file'].name,
        )
        from .tasks import process_excel_upload
        process_excel_upload.delay(upload.id)

    @action(detail=True, methods=['get'])
    def log(self, request, pk=None):
        upload = self.get_object()
        return Response({
            'id': upload.id,
            'status': upload.status,
            'processing_log': upload.processing_log,
            'records_imported': upload.records_imported,
            'records_errors': upload.records_errors,
        })

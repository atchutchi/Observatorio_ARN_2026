from django.utils import timezone
from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.permissions import IsARNStaff, IsOwnerOrARN
from .models import DataEntry, CumulativeData, FileUpload, ReceivedDocument
from .serializers import (
    DataEntrySerializer, BulkDataEntrySerializer,
    CumulativeDataSerializer, BulkCumulativeDataSerializer,
    FileUploadSerializer, FileUploadCreateSerializer,
    ReceivedDocumentSerializer, ReceivedDocumentCreateSerializer,
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
        qs = self.filter_queryset(self.get_queryset()).filter(
            is_validated=False,
            source__in=['manual', 'upload'],
        )
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            FileUploadSerializer(serializer.instance, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        user = self.request.user
        operator = serializer.validated_data.pop('operator', None)
        if user.is_operator_user:
            operator = user.operator
        elif not user.is_arn_staff:
            raise PermissionDenied('Não tem permissão para carregar ficheiros.')
        if operator is None:
            raise PermissionDenied('Seleccione o operador associado ao ficheiro.')

        upload = serializer.save(
            operator=operator,
            uploaded_by=user,
            original_filename=self.request.FILES['file'].name,
        )
        from .tasks import dispatch_excel_upload
        dispatch_excel_upload(upload.id)

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


class ReceivedDocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsARNStaff]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'operator__code', 'document_type', 'year', 'quarter',
        'status', 'priority', 'assigned_to',
    ]

    def get_queryset(self):
        return ReceivedDocument.objects.select_related(
            'operator', 'assigned_to', 'received_by',
        ).prefetch_related('imports').all()

    def get_serializer_class(self):
        if self.action == 'create':
            return ReceivedDocumentCreateSerializer
        return ReceivedDocumentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            ReceivedDocumentSerializer(serializer.instance, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        assigned_to = serializer.validated_data.get('assigned_to') or self.request.user
        serializer.save(
            assigned_to=assigned_to,
            received_by=self.request.user,
            original_filename=self.request.FILES['file'].name,
        )

    def perform_update(self, serializer):
        extra = {}
        if 'file' in self.request.FILES:
            extra['original_filename'] = self.request.FILES['file'].name
        serializer.save(**extra)

    @action(detail=True, methods=['post'])
    def send_to_import(self, request, pk=None):
        document = self.get_object()
        existing_import = document.imports.exclude(status='error').order_by('-uploaded_at').first()

        if existing_import:
            return Response({
                'detail': 'Este documento já tem uma importação activa ou concluída.',
                'upload': FileUploadSerializer(existing_import, context={'request': request}).data,
                'document': ReceivedDocumentSerializer(document, context={'request': request}).data,
            })

        upload = FileUpload.objects.create(
            operator=document.operator,
            uploaded_by=request.user,
            received_document=document,
            file=document.file.name,
            original_filename=document.original_filename,
            file_type=self._build_file_type(document),
            year=document.year,
            quarter=document.quarter,
            status='uploaded',
        )

        document.status = 'extracting'
        document.save(update_fields=['status', 'updated_at'])

        from .tasks import dispatch_excel_upload
        dispatch_excel_upload(upload.id)

        return Response({
            'detail': 'Documento enviado para importação.',
            'upload': FileUploadSerializer(upload, context={'request': request}).data,
            'document': ReceivedDocumentSerializer(document, context={'request': request}).data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        qs = self.filter_queryset(self.get_queryset())
        today = timezone.localdate()
        status_counts = {
            item['status']: item['total']
            for item in qs.values('status').annotate(total=Count('id'))
        }

        return Response({
            'total': qs.count(),
            'open': qs.exclude(status__in=['imported', 'archived']).count(),
            'overdue': qs.filter(
                due_date__lt=today,
            ).exclude(status__in=['imported', 'archived']).count(),
            'high_priority': qs.filter(priority='high').exclude(
                status__in=['imported', 'archived'],
            ).count(),
            'by_status': status_counts,
        })

    @staticmethod
    def _build_file_type(document):
        operator_code = document.operator.code.lower()
        if document.document_type == 'kpi_summary' and operator_code == 'orange':
            return 'kpi_orange'
        if document.document_type == 'questionnaire' and operator_code in {'telecel', 'orange', 'starlink'}:
            return f'questionnaire_{operator_code}'
        return 'other'

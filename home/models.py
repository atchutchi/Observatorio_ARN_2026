from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Operadora(models.Model):
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True)
    ativa = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Operadora'
        verbose_name_plural = 'Operadoras'
    
    def __str__(self):
        return self.nome

class TipoServico(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Tipo de Serviço'
        verbose_name_plural = 'Tipos de Serviços'
    
    def __str__(self):
        return self.nome

class DadoEstatistico(models.Model):
    operadora = models.ForeignKey(Operadora, on_delete=models.CASCADE)
    tipo_servico = models.ForeignKey(TipoServico, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    unidade = models.CharField(max_length=50, default='Unidade')
    data_referencia = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Dado Estatístico'
        verbose_name_plural = 'Dados Estatísticos'
    
    def __str__(self):
        return f"{self.operadora} - {self.tipo_servico}: {self.valor}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('info', 'Informação'),
        ('success', 'Sucesso'),
        ('warning', 'Aviso'),
        ('error', 'Erro'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    @classmethod
    def create_notification(cls, user, title, message, notification_type='info'):
        """Método auxiliar para criar notificações"""
        return cls.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type
        )

class UserActivity(models.Model):
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('data_upload', 'Upload de Dados'),
        ('report_generate', 'Geração de Relatório'),
        ('data_analysis', 'Análise de Dados'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Atividade do Usuário'
        verbose_name_plural = 'Atividades dos Usuários'
    
    def __str__(self):
        return f"{self.user.email} - {self.get_activity_type_display()}"
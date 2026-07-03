from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json
import uuid
import hashlib

class ReportTemplate(models.Model):
    """Templates de relatórios reutilizáveis"""
    REPORT_TYPES = [
        ('mercado', 'Relatório de Mercado'),
        ('dashboard_executivo', 'Dashboard Executivo'),
        ('comparativo', 'Análise Comparativa'),
        ('tendencias', 'Análise de Tendências'),
        ('trimestral', 'Relatório Trimestral'),
        ('anual', 'Relatório Anual'),
    ]
    
    FORMAT_TYPES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('html', 'HTML'),
        ('dashboard', 'Dashboard Interativo'),
    ]
    
    nome = models.CharField(max_length=200)
    tipo = models.CharField(max_length=50, choices=REPORT_TYPES)
    formato = models.CharField(max_length=20, choices=FORMAT_TYPES)
    configuracao = models.JSONField(default=dict)  # Configurações específicas do template
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Template de Relatório'
        verbose_name_plural = 'Templates de Relatórios'
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"

class GeneratedReport(models.Model):
    """Histórico de relatórios gerados"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('error', 'Erro'),
    ]
    
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    periodo_inicio = models.DateField()
    periodo_fim = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    arquivo_path = models.CharField(max_length=500, blank=True)
    parametros = models.JSONField(default=dict)  # Parâmetros usados na geração
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Relatório Gerado'
        verbose_name_plural = 'Relatórios Gerados'
    
    def __str__(self):
        return f"{self.titulo} - {self.created_at.strftime('%d/%m/%Y')}"

class ReportSchedule(models.Model):
    """Agendamento automático de relatórios"""
    FREQUENCY_CHOICES = [
        ('daily', 'Diário'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensal'),
        ('quarterly', 'Trimestral'),
        ('yearly', 'Anual'),
    ]
    
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE)
    nome = models.CharField(max_length=200)
    frequencia = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    hora = models.TimeField(default='08:00')
    dia_mes = models.IntegerField(null=True, blank=True)  # Para relatórios mensais/anuais
    destinatarios = models.JSONField(default=list)  # Lista de emails
    ativo = models.BooleanField(default=True)
    proximo_envio = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Agendamento de Relatório'
        verbose_name_plural = 'Agendamentos de Relatórios'
    
    def __str__(self):
        return f"{self.nome} ({self.get_frequencia_display()})"

class ChartConfiguration(models.Model):
    """Configurações de gráficos reutilizáveis"""
    CHART_TYPES = [
        ('line', 'Linha'),
        ('bar', 'Barras'),
        ('pie', 'Pizza'),
        ('doughnut', 'Rosquinha'),
        ('area', 'Área'),
        ('scatter', 'Dispersão'),
    ]
    
    nome = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=CHART_TYPES)
    configuracao = models.JSONField(default=dict)
    paleta_cores = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Configuração de Gráfico'
        verbose_name_plural = 'Configurações de Gráficos'
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"

class ReportAlert(models.Model):
    """Alertas baseados nos dados dos relatórios"""
    ALERT_TYPES = [
        ('threshold', 'Limite Atingido'),
        ('variation', 'Variação Significativa'),
        ('target', 'Meta Atingida'),
        ('anomaly', 'Anomalia Detectada'),
    ]
    
    nome = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=ALERT_TYPES)
    indicador = models.CharField(max_length=100)  # Nome do indicador a monitorar
    condicao = models.JSONField(default=dict)  # Condições do alerta
    destinatarios = models.JSONField(default=list)
    ativo = models.BooleanField(default=True)
    ultima_verificacao = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Alerta de Relatório'
        verbose_name_plural = 'Alertas de Relatórios'
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


# ===== MODELOS DO CHATBOT ARN =====

class ChatSession(models.Model):
    """Sessões de chat do usuário"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    inicio_sessao = models.DateTimeField(auto_now_add=True)
    fim_sessao = models.DateTimeField(null=True, blank=True)
    contexto = models.JSONField(default=dict)  # Contexto da conversa
    ativa = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-inicio_sessao']
        verbose_name = 'Sessão de Chat'
        verbose_name_plural = 'Sessões de Chat'
    
    def __str__(self):
        return f"Sessão {self.usuario.email}"

class ChatMessage(models.Model):
    """Mensagens individuais do chat"""
    MESSAGE_TYPES = [
        ('user', 'Usuário'),
        ('bot', 'Bot'),
        ('system', 'Sistema'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sessao = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='mensagens')
    tipo = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    mensagem = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    intencao_detectada = models.CharField(max_length=100, null=True, blank=True)
    confianca = models.FloatField(null=True, blank=True)
    dados_resposta = models.JSONField(null=True, blank=True)
    tempo_resposta = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Mensagem de Chat'
        verbose_name_plural = 'Mensagens de Chat'
    
    def __str__(self):
        return f"{self.get_tipo_display()}: {self.mensagem[:50]}..."

class ARNQueryCache(models.Model):
    """Cache de consultas para otimização"""
    query_hash = models.CharField(max_length=64, unique=True)
    resultado = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    validade = models.IntegerField(default=3600)  # Segundos
    hits = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Cache de Query ARN'
        verbose_name_plural = 'Cache de Queries ARN'
    
    def __str__(self):
        return f"Cache {self.query_hash[:8]}... ({self.hits} hits)"


class ChatIntent(models.Model):
    """Intenções detectadas e suas configurações"""
    INTENT_TYPES = [
        ('consulta_assinantes', 'Consulta de Assinantes'),
        ('analise_trafego', 'Análise de Tráfego'),
        ('mobile_money', 'Mobile Money'),
        ('market_share', 'Market Share'),
        ('tendencias', 'Análise de Tendências'),
        ('comparacao_operadores', 'Comparação de Operadores'),
        ('receitas', 'Análise de Receitas'),
        ('investimentos', 'Análise de Investimentos'),
        ('banda_larga', 'Banda Larga'),
        ('emprego', 'Análise de Emprego'),
        ('saudacao', 'Saudação'),
        ('despedida', 'Despedida'),
        ('nao_entendido', 'Não Entendido'),
    ]
    
    nome = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=50, choices=INTENT_TYPES)
    palavras_chave = models.JSONField(default=list)  # Lista de palavras-chave
    entidades_esperadas = models.JSONField(default=list)  # Entidades esperadas
    template_resposta = models.TextField()
    query_sql = models.TextField(blank=True)  # SQL template para consulta
    confianca_minima = models.FloatField(default=0.7)
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Intenção de Chat'
        verbose_name_plural = 'Intenções de Chat'
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"
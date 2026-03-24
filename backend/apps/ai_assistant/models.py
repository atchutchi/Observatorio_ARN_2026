from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='chat_sessions', verbose_name='Utilizador',
    )
    title = models.CharField(max_length=200, blank=True, verbose_name='Título')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sessão de Chat'
        verbose_name_plural = 'Sessões de Chat'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} — {self.title or 'Sem título'}"


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'Utilizador'),
        ('assistant', 'Assistente'),
    ]

    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE,
        related_name='messages', verbose_name='Sessão',
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name='Papel')
    content = models.TextField(verbose_name='Conteúdo')
    metadata = models.JSONField(default=dict, blank=True, verbose_name='Metadados')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mensagem de Chat'
        verbose_name_plural = 'Mensagens de Chat'
        ordering = ['created_at']

    def __str__(self):
        preview = self.content[:80]
        return f"[{self.role}] {preview}"

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
import datetime


class RegistroQuestionario(models.Model):
    """
    Modelo para registrar quando um questionário foi preenchido por um operador.
    """
    operadora = models.ForeignKey(
        'home.Operadora',
        on_delete=models.CASCADE,
        verbose_name=_("Operadora"),
        related_name="registros_questionario",
        null=True, blank=True  # Permitir nulo temporariamente para migrações
    )
    ano = models.PositiveIntegerField(
        verbose_name=_("Ano"),
        default=2025  # Valor padrão para o ano atual
    )
    trimestre = models.PositiveSmallIntegerField(
        verbose_name=_("Trimestre"),
        choices=[(1, '1º'), (2, '2º'), (3, '3º'), (4, '4º')],
        default=1  # Valor padrão para o primeiro trimestre
    )
    data_preenchimento = models.DateTimeField(
        verbose_name=_("Data de preenchimento"),
        default=datetime.datetime.now
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name=_("Usuário"),
        null=True, blank=True,
        related_name="questionarios_preenchidos"
    )
    
    class Meta:
        verbose_name = _("Registro de Questionário")
        verbose_name_plural = _("Registros de Questionários")
        unique_together = ('operadora', 'ano', 'trimestre')
        ordering = ['-ano', '-trimestre', 'operadora']
        
    def __str__(self):
        return f"{self.operadora or 'Sem operadora'} - {self.ano}/{self.trimestre}º trimestre" 
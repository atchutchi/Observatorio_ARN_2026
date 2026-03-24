from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin_arn', 'Administrador ARN'),
        ('analyst_arn', 'Analista ARN'),
        ('operator_telecel', 'Operador Telecel'),
        ('operator_orange', 'Operador Orange'),
        ('operator_starlink', 'Operador Starlink'),
        ('viewer', 'Visualizador'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='viewer',
        verbose_name='Papel',
    )
    operator = models.ForeignKey(
        'operators.Operator',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='users',
        verbose_name='Operador',
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    position = models.CharField(max_length=100, blank=True, verbose_name='Cargo')

    class Meta:
        verbose_name = 'Utilizador'
        verbose_name_plural = 'Utilizadores'
        ordering = ['username']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_arn_admin(self):
        return self.role == 'admin_arn'

    @property
    def is_arn_staff(self):
        return self.role in ('admin_arn', 'analyst_arn')

    @property
    def is_operator_user(self):
        return self.role in ('operator_telecel', 'operator_orange', 'operator_starlink')

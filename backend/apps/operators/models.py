from django.db import models


class OperatorType(models.Model):
    """
    Tipo/perfil de operador — determina quais indicadores se aplicam.
    Exemplos: terrestrial_full, satellite_isp, mvno, fixed_only
    """
    OPERATOR_TYPE_CHOICES = [
        ('terrestrial_full', 'Operador Terrestre Completo'),
        ('satellite_isp', 'Operador Satélite / ISP'),
        ('mvno', 'Operador Virtual (MVNO)'),
        ('fixed_only', 'Operador Fixo'),
    ]

    code = models.CharField(max_length=30, unique=True, verbose_name='Código')
    name = models.CharField(max_length=100, verbose_name='Nome')
    description = models.TextField(blank=True, verbose_name='Descrição')

    class Meta:
        verbose_name = 'Tipo de Operador'
        verbose_name_plural = 'Tipos de Operador'
        ordering = ['code']

    def __str__(self):
        return self.name


class Operator(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nome')
    legal_name = models.CharField(max_length=200, verbose_name='Razão Social')
    code = models.CharField(max_length=10, unique=True, verbose_name='Código')
    operator_type = models.ForeignKey(
        OperatorType,
        on_delete=models.PROTECT,
        related_name='operators',
        verbose_name='Tipo de Operador',
    )
    license_number = models.CharField(max_length=50, blank=True, verbose_name='Nº da Licença')
    contact_email = models.EmailField(blank=True, verbose_name='Email')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    director_name = models.CharField(max_length=200, blank=True, verbose_name='Director')
    address = models.TextField(blank=True, verbose_name='Endereço')
    logo = models.ImageField(upload_to='operators/logos/', blank=True, verbose_name='Logótipo')
    brand_color = models.CharField(
        max_length=7, default='#333333', verbose_name='Cor da Marca',
        help_text='Código hex, ex: #E30613'
    )
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    historical_names = models.JSONField(
        default=list, blank=True, verbose_name='Nomes Históricos',
        help_text='Nomes anteriores usados nos ficheiros Excel (ex: ["MTN", "Spacetel"])',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Operador'
        verbose_name_plural = 'Operadores'
        ordering = ['name']

    def __str__(self):
        return self.name

    @classmethod
    def resolve_name(cls, name):
        """Resolve historical names to the current operator (e.g. MTN → Telecel)"""
        name_upper = name.strip().upper()
        try:
            return cls.objects.get(code=name_upper)
        except cls.DoesNotExist:
            pass
        for op in cls.objects.all():
            for hist in op.historical_names:
                if hist.upper() == name_upper:
                    return op
        return None

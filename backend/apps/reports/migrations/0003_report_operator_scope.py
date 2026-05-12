import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operators', '0001_initial'),
        ('reports', '0002_report_docx_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='operator_scope',
            field=models.CharField(
                choices=[
                    ('all', 'Todos os operadores'),
                    ('operator', 'Operador específico'),
                    ('others', 'Outros operadores'),
                ],
                default='all',
                max_length=20,
                verbose_name='Âmbito de operadores',
            ),
        ),
        migrations.AddField(
            model_name='report',
            name='operator',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='reports',
                to='operators.operator',
                verbose_name='Operador',
            ),
        ),
    ]

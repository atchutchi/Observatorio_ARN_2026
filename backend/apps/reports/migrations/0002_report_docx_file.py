from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='docx_file',
            field=models.FileField(blank=True, upload_to='reports/docx/%Y/', verbose_name='Ficheiro Word'),
        ),
    ]

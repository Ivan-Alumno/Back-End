import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MascotasAPP', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clientes',
            old_name='apellido',
            new_name='apellido_paterno',
        ),
        migrations.AddField(
            model_name='clientes',
            name='apellido_materno',
            field=models.CharField(
                blank=True,
                default='',
                max_length=100,
                verbose_name='Apellido materno del cliente',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mascotas',
            name='añadido',
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name='Fecha de añadido',
            ),
            preserve_default=False,
        ),
    ]

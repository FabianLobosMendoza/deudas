from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('finanzas', '0005_alter_deuda_options_alter_entidad_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='gasto',
            name='medio_pago',
            field=models.CharField(
                choices=[
                    ('efectivo', 'Efectivo'),
                    ('debito', 'Debito'),
                    ('tarjeta', 'Tarjeta'),
                ],
                default='efectivo',
                help_text='efectivo/debito descuentan ahora; tarjeta se descuenta al pagar.',
                max_length=20,
            ),
        ),
    ]

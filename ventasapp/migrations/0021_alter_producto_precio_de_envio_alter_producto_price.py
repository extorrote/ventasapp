# Generated by Django 5.0.7 on 2025-07-07 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventasapp', '0020_producto_tiene_envio_gratis'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='precio_de_envio',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='producto',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
    ]

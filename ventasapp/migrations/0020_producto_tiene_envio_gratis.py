# Generated by Django 5.0.7 on 2025-07-07 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventasapp', '0019_remove_direcciondeenvio_propina_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='tiene_envio_gratis',
            field=models.BooleanField(default=False),
        ),
    ]

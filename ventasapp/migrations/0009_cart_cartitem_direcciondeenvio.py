# Generated by Django 5.0.7 on 2025-07-02 23:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventasapp', '0008_business_stripe_account_id'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(max_length=40, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField(default=1)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='ventasapp.cart')),
                ('extras', models.ManyToManyField(blank=True, to='ventasapp.extra')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ventasapp.producto')),
            ],
        ),
        migrations.CreateModel(
            name='DireccionDeEnvio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_completo', models.CharField(max_length=255)),
                ('telefono', models.CharField(max_length=20)),
                ('direccion', models.CharField(max_length=200)),
                ('ciudad', models.CharField(max_length=100)),
                ('estado', models.CharField(max_length=100)),
                ('codigo_postal', models.CharField(max_length=20)),
                ('opcion_entrega', models.CharField(choices=[('domicilio', 'Entrega a domicilio'), ('sucursal', 'Retiro en sucursal')], default='domicilio', max_length=100, verbose_name='¿Retiro en sucursal o prefieres entrega en casa?')),
                ('costo_envio', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

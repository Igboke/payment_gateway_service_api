# Generated by Django 5.2 on 2025-05-11 21:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Orders', '0005_alter_orderitem_product_alter_orders_client'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, help_text='Payment Amount', max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Successful'), ('failed', 'Failed')], default='pending', help_text='Payment Status', max_length=15)),
                ('transaction_ref', models.CharField(help_text='Internal transaction reference.', max_length=255, unique=True)),
                ('gateway_ref', models.CharField(help_text='Payment gateway transaction reference.', max_length=255, null=True, unique=True)),
                ('gateway_name', models.CharField(help_text='Payment gateway name.', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_payment', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_transaction', to='Orders.orders')),
            ],
            options={
                'verbose_name': 'Payment Transaction',
                'verbose_name_plural': 'Payment Transactions',
                'ordering': ['-created_at'],
            },
        ),
    ]

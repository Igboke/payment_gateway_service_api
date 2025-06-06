# Generated by Django 5.2 on 2025-05-10 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Orders', '0002_alter_orders_billing_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='total_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, help_text='Order Total', max_digits=10),
        ),
    ]

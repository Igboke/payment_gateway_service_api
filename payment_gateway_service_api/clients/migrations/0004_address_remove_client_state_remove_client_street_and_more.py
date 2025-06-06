# Generated by Django 5.2 on 2025-05-09 23:36

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0003_alter_client_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_line1', models.CharField(max_length=255)),
                ('street_line2', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(max_length=100)),
                ('state_province', models.CharField(max_length=100)),
                ('postal_code', models.CharField(max_length=20)),
                ('country', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='client',
            name='state',
        ),
        migrations.RemoveField(
            model_name='client',
            name='street',
        ),
        migrations.RemoveField(
            model_name='client',
            name='town',
        ),
        migrations.AddField(
            model_name='client',
            name='house_address',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='client', to='clients.address'),
            preserve_default=False,
        ),
    ]

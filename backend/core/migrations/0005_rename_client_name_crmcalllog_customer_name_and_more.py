# Generated by Django 5.2.4 on 2025-07-17 21:38

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_rename_crmcalllog_fields'),
    ]

    operations = [
        migrations.RenameField(
            model_name='crmcalllog',
            old_name='client_name',
            new_name='customer_name',
        ),
        migrations.AddField(
            model_name='crmcalllog',
            name='call_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='crmcalllog',
            name='notes',
            field=models.TextField(blank=True),
        ),
    ]

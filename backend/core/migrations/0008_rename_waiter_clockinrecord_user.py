# Generated by Django 5.2.4 on 2025-07-19 22:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_feedback_add_delivery_personnel'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clockinrecord',
            old_name='waiter',
            new_name='user',
        ),
    ]

# Generated by Django 5.1.2 on 2024-10-25 17:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='created_events',
            new_name='events',
        ),
    ]

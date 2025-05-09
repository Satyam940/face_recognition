# Generated by Django 5.2 on 2025-04-23 08:03

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fr", "0003_knownface_password"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="attendance",
            name="date",
        ),
        migrations.RemoveField(
            model_name="attendance",
            name="present",
        ),
        migrations.AddField(
            model_name="attendance",
            name="date_time",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name="attendance",
            name="status",
            field=models.BooleanField(default=False),
        ),
    ]

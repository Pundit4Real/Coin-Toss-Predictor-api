# Generated by Django 5.0.1 on 2024-01-23 08:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Api', '0006_rename_timestamp_prediction_predicted_at_customuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Api.customuser'),
        ),
    ]
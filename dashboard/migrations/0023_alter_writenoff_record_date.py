# Generated by Django 5.1.2 on 2024-11-11 09:05

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0022_alter_batch_record_date_alter_product_code_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="writenoff",
            name="record_date",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]

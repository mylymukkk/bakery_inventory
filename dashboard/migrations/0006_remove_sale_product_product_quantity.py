# Generated by Django 5.1.2 on 2024-10-18 23:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_sale_product_alter_product_code_alter_sale_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sale',
            name='product',
        ),
        migrations.AddField(
            model_name='product',
            name='quantity',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
    ]

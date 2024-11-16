# Generated by Django 5.1.2 on 2024-10-19 04:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_remove_sale_product_product_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batch',
            name='left',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='quantity',
            field=models.PositiveIntegerField(default=0, editable=False, null=True),
        ),
    ]

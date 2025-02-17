# Generated by Django 5.1.2 on 2024-10-17 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_sale_alter_batch_options_remove_product_quantity_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='product',
            field=models.ManyToManyField(through='dashboard.SaleItem', to='dashboard.product'),
        ),
        migrations.AlterField(
            model_name='product',
            name='code',
            field=models.DecimalField(decimal_places=0, max_digits=8, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='sale',
            name='number',
            field=models.DecimalField(decimal_places=0, max_digits=10, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='sale',
            name='total_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]

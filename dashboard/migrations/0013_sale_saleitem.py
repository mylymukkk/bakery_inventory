# Generated by Django 5.1.2 on 2024-10-30 01:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0012_remove_saleitem_sale_delete_sale_delete_saleitem"),
    ]

    operations = [
        migrations.CreateModel(
            name="Sale",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField()),
                (
                    "transaction_id",
                    models.DecimalField(
                        decimal_places=0, max_digits=50, null=True, unique=True
                    ),
                ),
                (
                    "total_price",
                    models.DecimalField(decimal_places=2, max_digits=10, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SaleItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "product_code",
                    models.DecimalField(
                        decimal_places=0, max_digits=8, null=True, unique=True
                    ),
                ),
                ("quantity", models.PositiveIntegerField(default=0, null=True)),
                (
                    "price",
                    models.DecimalField(decimal_places=2, max_digits=10, null=True),
                ),
                (
                    "sale",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="dashboard.sale",
                    ),
                ),
            ],
        ),
    ]

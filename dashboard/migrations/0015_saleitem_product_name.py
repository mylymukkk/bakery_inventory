# Generated by Django 5.1.2 on 2024-10-30 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0014_alter_saleitem_product_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="saleitem",
            name="product_name",
            field=models.CharField(max_length=50, null=True),
        ),
    ]

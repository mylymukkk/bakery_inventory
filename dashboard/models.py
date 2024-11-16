from typing import Any
from django.db import models
import datetime
from django.core.validators import MinLengthValidator

# Create your models here.
CATEGORY = [
    ('Bread', 'Bread'),
    ('Sweet Pastry', 'Sweet Pastry'),
    ('Savoury Pastry', 'Savoury Pastry'),
    ('Desserts', 'Desserts'),
    ('Beverages', 'Beverages'),
]

class Product(models.Model):
    name = models.CharField(max_length=50, unique=True, null = True)
    category = models.CharField(max_length=50, choices = CATEGORY)
    code = models.CharField(max_length=8, validators=[MinLengthValidator(8)], unique=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    quantity = models.PositiveIntegerField(default=0, editable=False, null=True)
        
    def __str__(self):
        return self.name
    
    def update_quantity(self):
        total_quantity = sum(batch.left for batch in Batch.objects.filter(product=self) if not batch.is_expired())
        self.quantity = total_quantity
        self.save()

    @classmethod
    def update_all_product_quantities(cls):
        for product in Product.objects.all():
            product.update_quantity()
        
            
class Batch(models.Model):
    record_date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0, null=True)
    left = models.PositiveIntegerField(null=True)
    expiry_date = models.DateField()

    class Meta:
        verbose_name_plural = 'Batches'

    def __str__(self):
        return self.product.name
    
    def save(self, *args, **kwargs):
        if not self.pk: 
            self.left = self.quantity
        super().save(*args, **kwargs)
        self.product.update_quantity()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.product.update_quantity()

    def is_expired(self):
        return self.expiry_date < datetime.date.today()
    
class WritenOff(models.Model):
    record_date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Batch, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0, null=True)

    def save(self, *args, **kwargs):
        if self.product.left < self.quantity:
            raise ValueError(f"Cannot write off more than available quantity ({self.product.left})")
        self.product.left -= self.quantity
        self.product.save()  
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} of {self.product} written off"


class Sale(models.Model):
    timestamp = models.DateTimeField()
    transaction_id = models.CharField(max_length=10, validators=[MinLengthValidator(10)], unique=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    def __str__(self):
        return str(self.transaction_id)

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product_code = models.CharField(max_length=8, validators=[MinLengthValidator(8)], null=True)
    product_name = models.CharField(max_length=50, null = True)
    quantity = models.PositiveIntegerField(default=0, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        return str(self.product_name)

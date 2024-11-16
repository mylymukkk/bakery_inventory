from django.contrib import admin
from .models import Product, Batch, Sale, SaleItem, WritenOff
from django.contrib.auth.models import Group

admin.site.site_header = 'BakeryInventory'

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'code', 'price')
    list_filter = ['category']

class BatchAdmin(admin.ModelAdmin):
    list_display = ('record_date', 'product', 'quantity', 'left', 'expiry_date')

class SaleAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'transaction_id', 'total_price')

class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product_code', 'product_name', 'quantity', 'price')
    list_filter = ['sale']

class WritenOffAdmin(admin.ModelAdmin):
    list_display = ('record_date', 'product', 'quantity')

# Register your models here.

admin.site.register(Product, ProductAdmin)
admin.site.register(Batch, BatchAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(SaleItem, SaleItemAdmin)
admin.site.register(WritenOff, WritenOffAdmin)

admin.site.unregister(Group)

from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name = 'dashboard-index'),
    path('products/', views.products, name = 'dashboard-products'),
    path('product/delete/<int:pk>/', views.product_delete, name = 'dashboard-product-delete'),
    path('product/edit/<int:pk>/', views.product_update, name = 'dashboard-product-update'),
    path('stock/', views.stock, name = 'dashboard-stock'),
    path('stock/batch/delete/<int:pk>/', views.batch_delete, name = 'dashboard-batch-delete'),
    path('stock/batch/edit/<int:pk>/', views.batch_update, name = 'dashboard-batch-update'),
    path('stock/batch/write-off/<int:pk>/', views.batch_write_off, name = 'dashboard-batch-write-off'),
    path('sales/', views.sales, name = 'dashboard-sales'),
    path('api/sales', views.receive_sales_data, name = 'receive-sales-data'),
    path('report/', views.report, name = 'dashboard-report'),

]
import datetime
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from dashboard.models import Product, Batch, Sale, SaleItem, WritenOff

class DashboardViewsTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username='admin', password='adminpass')
        self.user = User.objects.create_user(username='user', password='userpass')
        self.client = Client()

        self.product1 = Product.objects.create(name="Product 1", code='11111111', category="Category 1", price=10.0, quantity=100)
        self.product2 = Product.objects.create(name="Product 2", code='22222222', category="Category 2", price=20.0, quantity=50)
        self.product3 = Product.objects.create(name="Product 3", code='33333333', category="Category 1", price=30.0, quantity=200)

        self.batch1 = Batch.objects.create(product=self.product1, record_date=datetime.date.today() - datetime.timedelta(days=1), expiry_date=datetime.date.today() + datetime.timedelta(days=3), quantity=100, left=100)
        self.batch2 = Batch.objects.create(product=self.product2, record_date=datetime.date.today() - datetime.timedelta(days=6), expiry_date=datetime.date.today() + datetime.timedelta(days=3), quantity=50, left=50)
        
    def test_index_view_unauthenticated(self):
        response = self.client.get(reverse('dashboard-index'))
        self.assertRedirects(response, f"/?next={reverse('dashboard-index')}")

    def test_index_view_authenticated(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse('dashboard-index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/index.html')
        self.assertIn('items', response.context)
    
    def test_index_view_pagination_and_sorting(self):
        self.client.login(username='user', password='userpass')
        for i in range(12):
            Product.objects.create(name=f"Product {i+4}", code=f'{(i+4)*1111}', category="Category 1", price=10.0, quantity=100)
        
        response = self.client.get(reverse('dashboard-index'), {'page':2, 'sort':'name', 'order':'desc'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Product 1')
        self.assertNotContains(response, 'Product 3')

    def test_index_view_search_query(self):
            self.client.login(username='user', password='userpass')
            response = self.client.get(reverse('dashboard-index'), {'query': 'Product 1'})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Product 1')
            self.assertNotContains(response, 'Product 2')
            self.assertNotContains(response, 'Product 3')

            response = self.client.get(reverse('dashboard-index'), {'query': '11111111'})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Product 1')
            self.assertNotContains(response, 'Product 2')
            self.assertNotContains(response, 'Product 3')

    def test_index_view_partial_update(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse('dashboard-index'), {'query': 'Product 1'}, HTTP_HX_Request='true')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/index_table.html')



    def test_products_view_unauthenticated(self):
        response = self.client.get(reverse('dashboard-products'))
        self.assertRedirects(response, f"/?next={reverse('dashboard-products')}")

    def test_products_view_non_superuser(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse('dashboard-products'))
        self.assertEqual(response.status_code, 403) 

    def test_products_view_superuser(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('dashboard-products'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/products.html')
        self.assertIn('items', response.context)
        self.assertIn('form', response.context)

    def test_products_view_pagination_and_sorting(self):
            self.client.login(username='admin', password='adminpass')
            for i in range(12):
                Product.objects.create(name=f"Product {i+4}", code=f'{(i+4)*1111}', category="Category 1", price=10.0, quantity=100)
            
            response = self.client.get(reverse('dashboard-products'), {'page':2, 'sort':'name', 'order':'desc'})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Product 1')
            self.assertNotContains(response, 'Product 3')

    def test_products_view_search_query(self):
            self.client.login(username='admin', password='adminpass')
            response = self.client.get(reverse('dashboard-products'), {'query': 'Product 1'})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Product 1')
            self.assertNotContains(response, 'Product 2')
            self.assertNotContains(response, 'Product 3')

            response = self.client.get(reverse('dashboard-index'), {'query': 1111})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Product 1')
            self.assertNotContains(response, 'Product 2')
            self.assertNotContains(response, 'Product 3')

    def test_add_product(self):
            self.client.login(username='admin',password='adminpass')

            data = {
                'name': 'Product 4',
                'code': '44444444',
                'category': 'Bread',
                'price': 40.0,
                'quantity': 50
            }
            
            response = self.client.post(reverse('dashboard-products'), data)
            self.assertRedirects(response, reverse('dashboard-products'))
 
            response = self.client.get(reverse('dashboard-products'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Product 4')
             
    def test_add_product_invalid_data_missing_fields(self):
        self.client.login(username='admin', password='adminpass')
        
        data = {
            'code': '44444444',
            'category': 'Bread',
            'price': 40.0,
            'quantity': 50
        }
        response = self.client.post(reverse('dashboard-products'), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('name',  response.context['form'].errors)

    def test_add_product_invalid_data_duplicate_fields(self):
        self.client.login(username='admin', password='adminpass')
        
        data = {
            'name': 'Product 1',
            'code': '11111111',
            'category': 'Bread',
            'price': 15.0,
            'quantity': 25
        }
        response = self.client.post(reverse('dashboard-products'), data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('name', response.context['form'].errors)   
        self.assertIn('code', response.context['form'].errors)   
    
  

    def test_product_delete_unauthenticated(self):
        response = self.client.get(reverse('dashboard-product-delete', args=[self.product1.pk]))
        self.assertRedirects(response, f"/?next={reverse('dashboard-product-delete', args=[self.product1.pk])}")
    
    def test_product_delete_non_superuser(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse('dashboard-product-delete', args=[self.product1.pk]))
        self.assertEqual(response.status_code, 403)

    def test_product_delete_superuser(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('dashboard-product-delete', args=[self.product1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/product_delete.html')
        self.assertIn('item', response.context)
    
    def test_product_delete_post_request(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('dashboard-product-delete', args=[self.product1.pk]))
        self.assertRedirects(response, reverse('dashboard-products'))
        self.assertFalse(Product.objects.filter(id=self.product1.pk).exists())

    def test_product_delete_ivalid_pk(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('dashboard-product-delete', args=[999]))
        self.assertEqual(response.status_code, 404)
 
   
    def test_product_update_unauthenticated(self):
        response = self.client.get(reverse('dashboard-product-update', args=[self.product1.pk]))
        self.assertRedirects(response, f"/?next={reverse('dashboard-product-update', args=[self.product1.pk])}")  

    def test_product_update_non_superuser(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse('dashboard-product-update', args=[self.product1.pk]))
        self.assertEqual(response.status_code, 403)

    def test_product_update_superuser(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('dashboard-product-update', args=[self.product1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/product_update.html')
        self.assertIn('form', response.context)

    def test_product_update_post_valid_data(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(
            reverse('dashboard-product-update', args=[self.product1.pk]),
            {
                'name': 'Updated Product',
                'code': '11111111',
                'category': 'Bread',
                'price': 120.0
            }
        )

        self.assertRedirects(response, reverse('dashboard-products'))

        self.product1.refresh_from_db()
        self.assertEqual(self.product1.name, 'Updated Product')
        self.assertEqual(self.product1.category, 'Bread')
        self.assertEqual(self.product1.price, 120.0)
    
    def test_product_update_post_invalid_data(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(
            reverse('dashboard-product-update', args=[self.product1.pk]),
            {
                'name': '',
                'code': '1111',
                'category': 'Updated Category',
                'price': 100.0
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/product_update.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)

    def test_product_update_invalid_pk(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('dashboard-product-update', args=[999]))
        self.assertEqual(response.status_code, 404)



    def test_stock_view_unauthenticated(self):
        response = self.client.get(reverse('dashboard-stock'))
        self.assertRedirects(response, f"/?next={reverse('dashboard-stock')}")

    def test_stock_view_non_superuser(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse('dashboard-stock'))
        self.assertEqual(response.status_code, 403)

    def test_stock_view_superuser(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('dashboard-stock'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/stock.html')
        self.assertIn('items', response.context)
        self.assertIn('form', response.context)

    def test_stock_view_pagination_and_sorting(self):
        self.client.login(username='admin', password='adminpass')
        for i in range(12):
            Batch.objects.create(product=self.product1, record_date=datetime.date.today() - datetime.timedelta(days=i), expiry_date=datetime.date.today() + datetime.timedelta(days=i), quantity=100)
        
        response = self.client.get(reverse('dashboard-stock'), {'page': 1, 'sort': 'product__name', 'order': 'asc'})

      
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<th>Product 1</th>' )
        self.assertNotContains(response, '<th>Product 2</th>')
    
    def test_stock_view_search_query(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('dashboard-stock'), {'query': 'Product 1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<th>Product 1</th>')
        self.assertNotContains(response, '<th>Product 2</th>')

    def test_add_batch(self):
        self.client.login(username='admin', password='adminpass')
        
        data = {
            'product': '3',
            'record_date': datetime.date.today(),
            'expiry_date': datetime.date.today() + datetime.timedelta(days=30),
            'quantity': 200
        }
        
        response = self.client.post(reverse('dashboard-stock'), data)    
        self.assertRedirects(response, reverse('dashboard-stock'))

        response = self.client.get(reverse('dashboard-stock'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<th>Product 3</th>')

    def test_add_batch_invalid_data_missing_fields(self):
        self.client.login(username='admin', password='adminpass')
        
        data = {
            'quantity': 50
        }
        response = self.client.post(reverse('dashboard-products'), data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
    


    def test_batch_delete_unauthenticated(self):
        response = self.client.get(reverse('dashboard-batch-delete', args=[self.batch1.pk]))
        self.assertRedirects(response, f"/?next={reverse('dashboard-batch-delete', args=[self.batch1.pk])}")

    def test_batch_delete_non_superuser(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse('dashboard-batch-delete', args=[self.batch1.pk]))
        self.assertEqual(response.status_code, 403)

    def test_batch_delete_superuser(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('dashboard-batch-delete', args=[self.batch1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/batch_delete.html')
        self.assertIn('item', response.context)

    def test_batch_delete_post_request(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('dashboard-batch-delete', args=[self.batch1.pk]))
        self.assertRedirects(response, reverse('dashboard-stock'))
        self.assertFalse(Batch.objects.filter(id=self.batch1.pk).exists())
    
    def test_batch_delete_invalid_pk(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('dashboard-batch-delete', args=[999]))
        self.assertEqual(response.status_code, 404)



    def test_batch_update_unauthenticated(self):
        response = self.client.get(reverse('dashboard-batch-update', args=[self.batch1.pk]))
        self.assertRedirects(response, f"/?next={reverse('dashboard-batch-update', args=[self.batch1.pk])}")

    def test_batch_update_non_superuser(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse('dashboard-batch-update', args=[self.batch1.pk]))
        self.assertEqual(response.status_code, 403)

    def test_batch_update_superuser(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('dashboard-batch-update', args=[self.batch1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/batch_update.html')
        self.assertIn('form', response.context)

    def test_batch_update_post_valid_data(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(
            reverse('dashboard-batch-update', args=[self.batch1.pk]),
            {
                'product': '1',
                'record_date': datetime.date.today(),
                'expiry_date': datetime.date.today() + datetime.timedelta(days=20),
                'quantity': 60
            }
        )
        self.assertRedirects(response, reverse('dashboard-stock'))
        self.batch1.refresh_from_db()
        self.assertEqual(self.batch1.quantity, 60)

    def test_batch_update_post_invalid_data(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(
            reverse('dashboard-batch-update', args=[self.batch1.pk]),
            {
                'product': '1',
                'record_date': '',
                'expiry_date': '',
                'quantity': ''
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/batch_update.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)

    def test_batch_update_invalid_pk(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('dashboard-batch-update', args=[999]))
        self.assertEqual(response.status_code, 404)



    def test_batch_write_off_unauthenticated(self):
        response = self.client.get(reverse('dashboard-batch-write-off', args=[self.batch1.pk]))
        self.assertRedirects(response, f"/?next={reverse('dashboard-batch-write-off', args=[self.batch1.pk])}")

    def test_batch_write_off_non_superuser(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse('dashboard-batch-write-off', args=[self.batch1.pk]))
        self.assertEqual(response.status_code, 403)

    def test_batch_write_off_superuser(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('dashboard-batch-write-off', args=[self.batch1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/batch_write-off.html')
        self.assertIn('form', response.context)
        self.assertIn('item', response.context)

    def test_batch_write_off_post_valid_data(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(
            reverse('dashboard-batch-write-off', args=[self.batch1.pk]),
            {
                'quantity': 20
            }
        )
        self.assertRedirects(response, reverse('dashboard-stock'))

        self.batch1.refresh_from_db()
        self.assertEqual(self.batch1.left, 80)

        write_off_record = WritenOff.objects.filter(product=self.batch1).first()
        self.assertIsNotNone(write_off_record)
        self.assertEqual(write_off_record.quantity, 20)

    def test_batch_write_off_post_invalid_data(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(
            reverse('dashboard-batch-write-off', args=[self.batch1.pk]),
            {
                'quantity': 110
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/batch_write-off.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)

        self.assertFalse(WritenOff.objects.filter(product=self.batch1).exists())
        self.batch1.refresh_from_db()
        self.assertEqual(self.batch1.left, 100)

    def test_batch_write_off_invalid_pk(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('dashboard-batch-write-off', args=[999]))
        self.assertEqual(response.status_code, 404)



    def test_receive_sales_data_successful(self):
        sales_data = {
            "sales": [
                {
                    "transaction_id": "1234567890",
                    "total_price": 50.0,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "items": [
                        {
                            "product_code": "11111111",
                            "product_name": "Product 1",
                            "quantity": 5,
                            "price": 10.0
                        }
                    ]
                }
            ]
        }
        
        response = self.client.post(
            reverse('receive-sales-data'),
            data=json.dumps(sales_data),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        
        self.assertEqual(Sale.objects.count(), 1)
        self.assertEqual(SaleItem.objects.count(), 1)
        
        self.batch1.refresh_from_db()
        self.assertEqual(self.batch1.left, 95)

    def test_receive_sales_data_insufficient_batch_quantity(self):
        sales_data = {
            "sales": [
                {
                    "transaction_id": "1234567890",
                    "total_price": 500.0,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "items": [
                        {
                            "product_code": "11111111",
                            "product_name": "Product 1",
                            "quantity": 110, 
                            "price": 10.0
                        }
                    ]
                }
            ]
        }
        
        response = self.client.post(
            reverse('receive-sales-data'),
            data=json.dumps(sales_data),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        
        self.assertEqual(Sale.objects.count(), 1)
        self.assertEqual(SaleItem.objects.count(), 1)
        
        self.batch1.refresh_from_db()
        self.assertEqual(self.batch1.left, 0)

    def test_receive_sales_data_invalid_json(self):
        invalid_data = "{sales: [invalid JSON]}"
        
        response = self.client.post(
            reverse('receive-sales-data'),
            data=invalid_data,
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"status": "error", "message": "Invalid JSON"})
        
        self.assertEqual(Sale.objects.count(), 0)
        self.assertEqual(SaleItem.objects.count(), 0)

    def test_receive_sales_data_not_post(self):
        response = self.client.get(reverse('receive-sales-data'))
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {"status": "error", "message": "Only POST requests are allowed"})
        
        self.assertEqual(Sale.objects.count(), 0)
        self.assertEqual(SaleItem.objects.count(), 0)



    def test_sales_view_unauthenticated(self):
        response = self.client.get(reverse('dashboard-sales'))
        self.assertRedirects(response, f"/?next={reverse('dashboard-sales')}")

    def test_sales_view_authenticated(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse('dashboard-sales'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/sales.html')
        self.assertIn('items', response.context)

    def test_sales_view_pagination_and_sorting(self):
        self.client.login(username='user', password='userpass')
        for i in range(9):
            sale = Sale.objects.create(
                transaction_id=f"123456789{i+1}",
                total_price=100 + i * 10,
                timestamp=datetime.datetime.today()
            )
            SaleItem.objects.create(
                sale=sale,
                product_name=f"Product {i+1}",
                product_code=f"{10000000 + i}",
                quantity=i + 1,
                price=10.0
            )
           
        
        response = self.client.get(reverse('dashboard-sales'), {'page':2, 'sort':'transaction_id', 'order':'asc'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['items']), 1)
        self.assertContains(response, '1234567899')
        self.assertNotContains(response, '1234567891')

    def test_sales_view_search_query(self):
        self.client.login(username='user', password='userpass')
        for i in range(3):
            sale = Sale.objects.create(
                transaction_id=f"123456789{i+1}",
                total_price=100 + i * 10,
                timestamp=datetime.datetime.today()
            )
            SaleItem.objects.create(
                sale=sale,
                product_name=f"Product {i+1}",
                product_code=f"{10000000 + i}",
                quantity=i + 1,
                price=10.0
            )
        response = self.client.get(reverse('dashboard-sales'), {'query': '1234567891'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1234567891')
        self.assertNotContains(response, '1234567892')

    def test_sales_view_partial_reload(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse('dashboard-sales'), HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/sales_table.html')



    def test_report_view_unauthenticated(self):
        response = self.client.get(reverse('dashboard-report'))
        self.assertRedirects(response, f"/?next={reverse('dashboard-report')}")

    def test_report_view_authenticated(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse('dashboard-report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/report.html')
        self.assertIn('items', response.context)

    def test_report_view_partial_reload(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse('dashboard-report'), HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/report_table.html')
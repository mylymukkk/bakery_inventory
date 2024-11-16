from django.test import TestCase
from django.utils import timezone
from dashboard.models import Product, Batch, WritenOff, Sale, SaleItem
import datetime


class ProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Bread",
            category="Bread",
            code='12345678',
            price=20.5,
            quantity=0
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Bread")
        self.assertEqual(self.product.category, "Bread")
        self.assertEqual(self.product.code, '12345678')
        self.assertEqual(self.product.price, 20.5)

    def test_update_quantity_method(self):
        batch1 = Batch.objects.create(
            product=self.product,
            quantity=10,
            left=10,
            expiry_date=datetime.date.today() + datetime.timedelta(days=5))
        batch2 = Batch.objects.create(
            product=self.product,
            quantity=5,
            left=5,
            expiry_date=datetime.date.today() - datetime.timedelta(days=1))
        self.product.update_quantity()
        
        self.assertEqual(self.product.quantity, 10)

    def test_update_all_product_quantities(self):
        Batch.objects.create(
            product=self.product,
            quantity=15,
            left=15,
            expiry_date=datetime.date.today() + datetime.timedelta(days=5))
        Product.update_all_product_quantities()
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 15)


class BatchModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Bread",
            category="Bread",
            code='12345678',
            price=20.5)

    def test_batch_creation(self):
        batch = Batch.objects.create(
            product=self.product,
            quantity=20,
            expiry_date=datetime.date.today() + datetime.timedelta(days=10))
        self.assertEqual(batch.product.name, "Test Bread")
        self.assertEqual(batch.product.code, '12345678')
        self.assertEqual(batch.quantity, 20)
        self.assertEqual(batch.left, 20)
        self.assertEqual(batch.expiry_date, datetime.date.today() + datetime.timedelta(days=10))

    def test_is_expired_method(self):
        expired_batch = Batch.objects.create(
            product=self.product,
            quantity=10,
            expiry_date=datetime.date.today() - datetime.timedelta(days=1))
        valid_batch = Batch.objects.create(
            product=self.product,
            quantity=10,
            expiry_date=datetime.date.today() + datetime.timedelta(days=1))
        self.assertTrue(expired_batch.is_expired())
        self.assertFalse(valid_batch.is_expired())

    def test_update_quantity_on_batch_save(self):
        batch = Batch.objects.create(
            product=self.product,
            quantity=20,
            left=20,
            expiry_date=datetime.date.today() + datetime.timedelta(days=10))
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 20)

    def test_update_quantity_on_batch_delete(self):
        batch = Batch.objects.create(
            product=self.product,
            quantity=20,
            left=20,
            expiry_date=datetime.date.today() + datetime.timedelta(days=10))
        batch.delete()
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 0)


class WritenOffModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Bread",
            category="Bread",
            code='12345678',
            price=20.5)
        self.batch = Batch.objects.create(
            product=self.product,
            quantity=10,
            left=10,
            expiry_date=datetime.date.today() + datetime.timedelta(days=10))

    def test_write_off_successful(self):
        writen_off = WritenOff.objects.create(
            product=self.batch,
            quantity=5)
        self.batch.refresh_from_db()
        self.assertEqual(self.batch.left, 5)

    def test_write_off_exceeds_left_quantity(self):
        with self.assertRaises(ValueError):
            WritenOff.objects.create(
                product=self.batch,
                quantity=15)


class SaleModelTest(TestCase):
    def setUp(self):
        self.sale = Sale.objects.create(
            timestamp=datetime.datetime.now(),
            transaction_id='111222333',
            total_price=50.0
        )

    def test_sale_creation(self):
        self.assertEqual(self.sale.transaction_id, '111222333')
        self.assertEqual(self.sale.total_price, 50.0)


class SaleItemModelTest(TestCase):
    def setUp(self):
        self.sale = Sale.objects.create(
            timestamp=datetime.datetime.now(), 
            transaction_id='1234567890',
            total_price=50.0)
        self.sale_item = SaleItem.objects.create(
            sale=self.sale,
            product_code='12345678',
            product_name="Test Product",
            quantity=2,
            price=25.0
        )

    def test_sale_item_creation(self):
        self.assertEqual(self.sale_item.product_name, "Test Product")
        self.assertEqual(self.sale_item.product_code,'12345678')
        self.assertEqual(self.sale_item.quantity, 2)
        self.assertEqual(self.sale_item.price, 25.0)

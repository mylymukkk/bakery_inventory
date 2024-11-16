from django.test import TestCase
from dashboard.forms import CreateProduct, CreateBatch, UpdateBatch, WriteOffProduct
from dashboard.models import Product, Batch
from django.utils import timezone
import datetime


class CreateProductFormTest(TestCase):
    def test_create_product_form_valid_data(self):
        form = CreateProduct(data={
            'name': 'Test Product',
            'code': 12345678,
            'category': 'Bread',
            'price': 10.0,
        })
        self.assertTrue(form.is_valid())

    def test_create_product_form_invalid_data(self):
        form = CreateProduct(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('code', form.errors)
        self.assertIn('price', form.errors)


class CreateBatchFormTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Bread", category="Bread",
            code=12345678,
            price=20.5)

    def test_create_batch_form_valid_data(self):
        form = CreateBatch(data={
            'product': self.product.id,
            'quantity': 10,
            'expiry_date': timezone.now().date() + datetime.timedelta(days=5)
        })
        self.assertTrue(form.is_valid())

    def test_create_batch_form_invalid_expiry_date(self):
        form = CreateBatch(data={
            'product': self.product.id,
            'quantity': -10,
            'expiry_date': 'invalid-date'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)
        self.assertIn('expiry_date', form.errors)


class UpdateBatchFormTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Bread", category="Bread",
            code=12345678,
            price=20.5)
        self.batch = Batch.objects.create(
            product=self.product, 
            quantity=20,
            expiry_date=timezone.now().date() + datetime.timedelta(days=10))

    def test_update_batch_form_valid_data(self):
        form = UpdateBatch(data={
            'product': self.product.id,
            'quantity': 15,
            'expiry_date': timezone.now().date() + datetime.timedelta(days=5)
        })
        self.assertTrue(form.is_valid())

    def test_update_batch_form_invalid_quantity(self):
        form = UpdateBatch(data={
            'product': self.product.id,
            'quantity': -5,
            'expiry_date': timezone.now().date() + datetime.timedelta(days=5)
        })
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)


class WriteOffProductFormTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Bread", 
            category="Bread",
            code=12345678,
            price=20.5)
        self.batch = Batch.objects.create(
            product=self.product, 
            quantity=10,
            left=10,
            expiry_date=timezone.now().date() + datetime.timedelta(days=5))

    def test_write_off_product_form_valid_quantity(self):
        form = WriteOffProduct(data={'quantity': 5}, batch=self.batch)
        self.assertTrue(form.is_valid())

    def test_write_off_product_form_invalid_quantity(self):
        form = WriteOffProduct(data={'quantity': 15}, batch=self.batch)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)

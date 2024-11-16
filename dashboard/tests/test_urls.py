from django.test import SimpleTestCase
from django.urls import reverse, resolve
from dashboard import views

class DashboardURLsTest(SimpleTestCase):

    def test_index_url_resolves(self):
        url = reverse('dashboard-index')
        self.assertEqual(resolve(url).func, views.index)

    def test_products_url_resolves(self):
        url = reverse('dashboard-products')
        self.assertEqual(resolve(url).func, views.products)

    def test_product_delete_url_resolves(self):
        url = reverse('dashboard-product-delete', args=[1])
        self.assertEqual(resolve(url).func, views.product_delete)

    def test_product_update_url_resolves(self):
        url = reverse('dashboard-product-update', args=[1])
        self.assertEqual(resolve(url).func, views.product_update)

    def test_stock_url_resolves(self):
        url = reverse('dashboard-stock')
        self.assertEqual(resolve(url).func, views.stock)

    def test_batch_delete_url_resolves(self):
        url = reverse('dashboard-batch-delete', args=[1])
        self.assertEqual(resolve(url).func, views.batch_delete)

    def test_batch_update_url_resolves(self):
        url = reverse('dashboard-batch-update', args=[1])
        self.assertEqual(resolve(url).func, views.batch_update)

    def test_batch_write_off_url_resolves(self):
        url = reverse('dashboard-batch-write-off', args=[1])
        self.assertEqual(resolve(url).func, views.batch_write_off)

    def test_sales_url_resolves(self):
        url = reverse('dashboard-sales')
        self.assertEqual(resolve(url).func, views.sales)

    def test_receive_sales_data_url_resolves(self):
        url = reverse('receive-sales-data')
        self.assertEqual(resolve(url).func, views.receive_sales_data)

    def test_report_url_resolves(self):
        url = reverse('dashboard-report')
        self.assertEqual(resolve(url).func, views.report)

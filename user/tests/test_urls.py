from django.test import SimpleTestCase
from django.urls import reverse, resolve
from user import views
from django.contrib.auth.views import LoginView, LogoutView

class UserURLsTest(SimpleTestCase):

    def test_register_url_resolves(self):
        url = reverse('user-register')
        self.assertEqual(resolve(url).func, views.register)

    def test_login_url_resolves(self):
        url = reverse('user-login')
        self.assertEqual(resolve(url).func.view_class, LoginView)

    def test_logout_url_resolves(self):
        url = reverse('user-logout')
        self.assertEqual(resolve(url).func.view_class, LogoutView)

    def test_profile_url_resolves(self):
        url = reverse('user-profile')
        self.assertEqual(resolve(url).func, views.profile)

    def test_profile_update_url_resolves(self):
        url = reverse('user-profile-update')
        self.assertEqual(resolve(url).func, views.profile_update)

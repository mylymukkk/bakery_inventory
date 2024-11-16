from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from user.forms import RegistrationForm, UpdateUserForm

class RegisterViewTest(TestCase):
    def test_register_view_get(self):
        response = self.client.get(reverse('user-register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/register.html')
        self.assertIsInstance(response.context['form'], RegistrationForm)

    def test_register_view_post_valid_data(self):
        response = self.client.post(reverse('user-register'), data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPassword123',
            'password2': 'ComplexPassword123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user-login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_view_post_invalid_data(self):
        response = self.client.post(reverse('user-register'), data={
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'ComplexPassword123',
            'password2': 'DifferentPassword123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/register.html')
        self.assertFalse(User.objects.filter(username='newuser').exists())
        self.assertIn('email', response.context['form'].errors)
        self.assertIn('password2', response.context['form'].errors)


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_profile_view_get_authenticated(self):
        response = self.client.get(reverse('user-profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/profile.html')

    def test_profile_view_get_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('user-profile'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('user-login')}?next={reverse('user-profile')}")


class ProfileUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password', email='testuser@example.com')
        self.client.login(username='testuser', password='password')

    def test_profile_update_view_get(self):
        response = self.client.get(reverse('user-profile-update'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/profile_update.html')
        self.assertIsInstance(response.context['form'], UpdateUserForm)

    def test_profile_update_view_post_valid_data(self):
        response = self.client.post(reverse('user-profile-update'), data={
            'username': 'updateduser',
            'email': 'updateduser@example.com',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user-profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')
        self.assertEqual(self.user.email, 'updateduser@example.com')

    def test_profile_update_view_post_invalid_data(self):
        response = self.client.post(reverse('user-profile-update'), data={
            'username': 'updateduser',
            'email': 'invalid-email',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/profile_update.html')
        self.assertIn('email', response.context['form'].errors)

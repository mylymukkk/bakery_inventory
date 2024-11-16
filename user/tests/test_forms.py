from django.test import TestCase
from user.forms import RegistrationForm, UpdateUserForm
from django.contrib.auth.models import User


class RegistrationFormTest(TestCase):
    def setUp(self):
        User.objects.create_user(
            username='existinguser', 
            email='existinguser@example.com', 
            password='password123')
        
    def test_registration_form_valid_data(self):
        form = RegistrationForm(data={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'ComplexPassword123',
            'password2': 'ComplexPassword123',
        })
        self.assertTrue(form.is_valid())

    def test_registration_form_existing_username(self):
        form = RegistrationForm(data={
            'username': 'existinguser',
            'email': 'testuser@example.com',
            'password1': 'ComplexPassword123',
            'password2': 'ComplexPassword123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    # def test_registration_form_existing_email(self):
    #     form = RegistrationForm(data={
    #         'username': 'testuser',
    #         'email': 'existinguser@example.com',  
    #         'password1': 'ComplexPassword123',
    #         'password2': 'ComplexPassword123',
    #     })
    #     self.assertFalse(form.is_valid())
    #     self.assertIn('email', form.errors)

    def test_registration_form_invalid_email(self):
        form = RegistrationForm(data={
            'username': 'testuser',
            'email': 'invalid-email',
            'password1': '1234',
            'password2': '1234',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('password2', form.errors)

    def test_registration_form_password_mismatch(self):
        form = RegistrationForm(data={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'ComplexPassword123',
            'password2': 'DifferentPassword123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class UpdateUserFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            email='testuser@example.com')
        User.objects.create_user(
            username='existinguser', 
            email='existinguser@example.com', 
            password='password123')

    def test_update_user_form_valid_data(self):
        form = UpdateUserForm(data={
            'username': 'updateduser',
            'email': 'updateduser@example.com',
        }, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_update_user_form_existing_username(self):
        form = UpdateUserForm(data={
            'username': 'existinguser',
            'email': 'updateduser@example.com',
        }, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    # def test_update_user_form_existing_email(self):
    #     form = UpdateUserForm(data={
    #         'username': 'updateduser',
    #         'email': 'existinguser@example.com',
    #     }, instance=self.user)
    #     self.assertFalse(form.is_valid())
    #     self.assertIn('email', form.errors)

    def test_update_user_form_invalid_email(self):
        form = UpdateUserForm(data={
            'username': 'updateduser',
            'email': 'invalid-email',
        }, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

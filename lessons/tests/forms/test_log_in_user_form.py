from django.test import TestCase
from lessons.forms.user_forms import *
from django import forms

class LoginUserFormTestCase(TestCase):
    """
    Contains the test cases for the login form
    """

    def setUp(self):
        """
        Simulate the form input
        """
        self.form_input = { 
            'email': 'janedoe@example.com',
            'password': 'Password123' }

    """
    Test cases
    """

    def test_form_contains_required_fields(self):
        form = LoginUserForm()
        self.assertIn('email', form.fields)
        self.assertIn('password', form.fields)
        password_field = form.fields['password']
        self.assertTrue(isinstance(password_field.widget, forms.PasswordInput))

    def test_form_accepts_valid_input(self):
        form = LoginUserForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_email(self):
        self.form_input['email'] = ''
        form = LoginUserForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_password(self):
        self.form_input['password'] = ''
        form = LoginUserForm(data=self.form_input)
        self.assertFalse(form.is_valid())
    
    def test_form_rejects_incorrect_email(self):
        self.form_input['email'] = 'incorrectemail@'
        form = LoginUserForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_incorrect_password(self):
        """
        It accepts an incorrect password so that potential attacks don't get information on validation schema
        """
        self.form_input['password'] = 'pswd'
        form = LoginUserForm(data=self.form_input)
        self.assertTrue(form.is_valid())
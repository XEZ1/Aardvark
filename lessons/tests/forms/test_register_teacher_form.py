from django.test import TestCase
from lessons.models.user_models import User, TeacherProfile, UserType
from lessons.forms.user_forms import *
from django import forms
from django.contrib.auth.hashers import check_password

class RegisterTeacherFormTestCase(TestCase):
    """
    Contains the test cases for the teacher registration form
    """

    def setUp(self):
        """
        Simulate the form input
        """
        self.form_input = {
            'first_name': 'Jane',
            'last_name' : 'Doe',
            'email' : 'janedoe@example.com',
            'password' : 'Password123',
            'password_confirm' : 'Password123' }

    """
    Test cases
    """
    def test_valid_teacher_registration_form(self):
        form = RegisterTeacherForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = RegisterTeacherForm()

        # Check that first_name and last_name fields are present
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        
        # Check that the email field is present and of correct type
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))

        # Check that the password field is present and of correct type
        self.assertIn('password', form.fields)
        password_widget = form.fields['password'].widget
        self.assertTrue(isinstance(password_widget, forms.PasswordInput))

        # Check that the email field is present and of correct type
        self.assertIn('password_confirm', form.fields)
        password_confirm_widget = form.fields['password_confirm'].widget
        self.assertTrue(isinstance(password_confirm_widget, forms.PasswordInput))

    def test_form_uses_model_validation(self):
        self.form_input['email'] = 'bademail'
        form = RegisterTeacherForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_uppercase_character(self):
        self.form_input['password'] = 'password123'
        self.form_input['password_confirm'] = 'password123'
        form = RegisterTeacherForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        self.form_input['password_confirm'] = 'PASSWORD123'
        form = RegisterTeacherForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['password'] = 'PasswordABC'
        self.form_input['password_confirm'] = 'PasswordABC'
        form = RegisterTeacherForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_confirm_password_must_be_equal(self):
        self.form_input['password_confirm'] = 'Paassword123'
        form = RegisterTeacherForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_username_set_to_email(self):
        form = RegisterTeacherForm(data=self.form_input)
        form.save()
        
        teacher_user = User.objects.get(email = 'janedoe@example.com')
        self.assertTrue(teacher_user.username == 'janedoe@example.com')

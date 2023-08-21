from django.test import TestCase
from lessons.models.user_models import User, StudentProfile, UserType
from lessons.forms.user_forms import *
from django import forms
from django.contrib.auth.hashers import check_password

class RegisterStudentFormTestCase(TestCase):
    """
    Contains the test cases for the student registration form
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

    def test_valid_student_registration_form(self):
        form = RegisterStudentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = RegisterStudentForm()

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
        form = RegisterStudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_uppercase_character(self):
        self.form_input['password'] = 'password123'
        self.form_input['password_confirm'] = 'password123'
        form = RegisterStudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        self.form_input['password_confirm'] = 'PASSWORD123'
        form = RegisterStudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['password'] = 'PasswordABC'
        self.form_input['password_confirm'] = 'PasswordABC'
        form = RegisterStudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_confirm_password_must_be_equal(self):
        self.form_input['password_confirm'] = 'Paassword123'
        form = RegisterStudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_username_set_to_email(self):
        form = RegisterStudentForm(data=self.form_input)
        form.save()
        
        user = User.objects.get(email = 'janedoe@example.com')
        self.assertTrue(user.username == 'janedoe@example.com')

    def test_form_must_save_correctly(self):
        form = RegisterStudentForm(data=self.form_input)

        before_user_count = User.objects.count()
        before_profile_count = StudentProfile.objects.count()
        form.save()
        after_user_count = User.objects.count()
        after_profile_count = StudentProfile.objects.count()

        self.assertEqual(before_user_count, after_user_count - 1)
        self.assertEqual(before_profile_count, after_profile_count - 1)

        user = User.objects.get(username = 'janedoe@example.com')
        
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.com')
        self.assertEqual(user.type, UserType.STUDENT)
        self.assertEqual(user.is_active, True)
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
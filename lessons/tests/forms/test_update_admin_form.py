from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models.user_models import User, AdminProfile, UserType
from lessons.forms.user_forms import *
from django import forms
from django.contrib.auth.hashers import check_password
from lessons.tests.helpers import LoginHelper

class UpdateAdminFormTestCase(TestCase, LoginHelper):
    """
    Contains the test cases for the update admin form
    """

    def setUp(self):
        """
        Simulate the form input
        """

        self._create_admin_user()
        self.form_input = {
            'first_name': 'JaneNew',
            'last_name' : 'DoeNew',
            'email' : 'janedoe@example.com',
            'password' : 'Password1234',
            'password_confirm' : 'Password1234' }

    """
    Test cases
    """

    def test_valid_update_admin_form(self):
        """
        Check that form valid
        """
        form = UpdateAdminForm(data=self.form_input, instance=self.admin_user)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        """
        Check that admin update form has necessary field filled out
        """
        form = UpdateAdminForm()

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

    def test_form_must_accept_empty_password_fields(self):
        """
        Admin can be updated without having to change the users password
        """
        self.form_input['password'] = ''
        self.form_input['password_confirm'] = ''
        form = UpdateAdminForm(data=self.form_input, instance=self.admin_user)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['first_name'] = ''
        form = UpdateAdminForm(data=self.form_input, instance=self.admin_user)
        self.assertFalse(form.is_valid())

    def test_form_reject_existing_director_email_address(self):
        """
        If director with same email exists, email is invalid 
        """
        self._create_director_user()
        self.form_input['email'] = 'director@example.com'
        form = UpdateAdminForm(data=self.form_input, instance=self.admin_user)
        self.assertFalse(form.is_valid())

    def test_form_reject_existing_student_email_address(self):
        """
        If student with same email exists, email is invalid 
        """
        self._create_student_user()
        self.form_input['email'] = 'student@example.com'
        form = UpdateAdminForm(data=self.form_input, instance=self.admin_user)
        self.assertFalse(form.is_valid())

    def test_form_reject_existing_teacher_email_address(self):
        """
        If teacher with same email exists, email is invalid 
        """
        self._create_teacher_user()
        self.form_input['email'] = 'teacher@example.com'
        form = UpdateAdminForm(data=self.form_input, instance=self.admin_user)
        self.assertFalse(form.is_valid())

    def test_form_reject_existing_admin_email_address(self):
        """
        If another admin user with same email exists, email is invalid 
        """
        # Create second admin user
        User.objects.create_user(
            'admin2@example.com',
            first_name='Jane',
            last_name='Doe',
            email='admin2@example.com',
            password='Password123',
            type=UserType.ADMIN,
            is_active=True)

        self.form_input['email'] = 'admin2@example.com'
        form = UpdateAdminForm(data=self.form_input, instance=self.admin_user)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_uppercase_character(self):
        """
        Password must have atleast one uppercase character
        """
        self.form_input['password'] = 'password123'
        self.form_input['password_confirm'] = 'password123'
        form = UpdateAdminForm(data=self.form_input, instance=self.admin_user)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        """
        Password must have atleast one lowercase character
        """
        self.form_input['password_confirm'] = 'PASSWORD123'
        form = UpdateAdminForm(data=self.form_input, instance=self.admin_user)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        """
        Password must have atleast one number
        """
        self.form_input['password'] = 'PasswordABC'
        self.form_input['password_confirm'] = 'PasswordABC'
        form = UpdateAdminForm(data=self.form_input, instance=self.admin_user)
        self.assertFalse(form.is_valid())

    def test_new_password_and_confirm_password_must_be_equal(self):
        """
        New value in confirm password must be the same as password
        """
        self.form_input['password_confirm'] = 'Paassword123'
        form = UpdateAdminForm(data=self.form_input, instance=self.admin_user)
        self.assertFalse(form.is_valid())

    def test_form_must_save_with_new_password_correctly(self):
        """
        New password must save when admin form is updated
        """
        form = UpdateAdminForm(data=self.form_input, instance=self.admin_user)

        before_user_count = User.objects.count()
        before_profile_count = AdminProfile.objects.count()
        form.save()
        after_user_count = User.objects.count()
        after_profile_count = AdminProfile.objects.count()

        # No additions should take place.
        self.assertEqual(before_user_count, after_user_count)
        self.assertEqual(before_profile_count, after_profile_count)

        with self.assertRaises(User.DoesNotExist): 
            User.objects.get(username = 'admin@example.com')

        user = User.objects.get(username = 'janedoe@example.com')
        self.assertEqual(user.first_name, 'JaneNew')
        self.assertEqual(user.last_name, 'DoeNew')
        self.assertEqual(user.email, 'janedoe@example.com')
        self.assertEqual(user.type, UserType.ADMIN)
        self.assertEqual(user.is_active, True)
        is_password_correct = check_password('Password1234', user.password)
        self.assertTrue(is_password_correct)

    def test_form_must_save_with_no_password_correctly(self):
        """
        Form with empty password should leave the password unchanged
        """
        self.form_input['password'] = ''
        self.form_input['password_confirm'] = ''
        form = UpdateAdminForm(data=self.form_input, instance=self.admin_user)

        # Count should stay the same
        before_user_count = User.objects.count()
        before_profile_count = AdminProfile.objects.count()
        form.save()
        after_user_count = User.objects.count()
        after_profile_count = AdminProfile.objects.count()

        # No additions should take place.
        self.assertEqual(before_user_count, after_user_count)
        self.assertEqual(before_profile_count, after_profile_count)

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username = 'admin@example.com')

        user = User.objects.get(username = 'janedoe@example.com')
        self.assertEqual(user.first_name, 'JaneNew')
        self.assertEqual(user.last_name, 'DoeNew')
        self.assertEqual(user.email, 'janedoe@example.com')
        self.assertEqual(user.type, UserType.ADMIN)
        self.assertEqual(user.is_active, True)

        # Password remains unchanged
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)

    def test_form_must_save_with_elevated_permissions_correctly(self):
        """
        Admin account can be elevated to director account
        """
        self.form_input['make_director'] = True
        form = UpdateAdminForm(data=self.form_input, instance=self.admin_user)

        before_user_count = User.objects.count()
        before_profile_count = AdminProfile.objects.count()
        form.save()
        after_user_count = User.objects.count()
        after_profile_count = AdminProfile.objects.count()

        # No additions should take place.
        self.assertEqual(before_user_count, after_user_count)
        self.assertEqual(before_profile_count, after_profile_count)

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username = 'admin@example.com')

        user = User.objects.get(username = 'janedoe@example.com')
        self.assertEqual(user.first_name, 'JaneNew')
        self.assertEqual(user.last_name, 'DoeNew')
        self.assertEqual(user.email, 'janedoe@example.com')
        self.assertEqual(user.type, UserType.DIRECTOR)
        self.assertEqual(user.is_active, True)

        # Password remains unchanged
        is_password_correct = check_password('Password1234', user.password)
        self.assertTrue(is_password_correct)

    
from django.test import TestCase
from lessons.models.user_models import User, UserType, AdminProfile
from lessons.forms.user_forms import *
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from ..helpers import LoginHelper
from django.contrib import messages

class UpdateAdminViewTestCase(TestCase, LoginHelper):
    """
    Contains the test cases for the update admin view
    """

    def setUp(self):
        """
        Generate admin user that will be deleted.
        """
        self._create_admin_user()
        self._create_director_user()
        self.url = reverse('update_admin', kwargs={ 'email': self.admin_user.username })

        self.form_input = {
            'first_name': 'JaneNew',
            'last_name' : 'DoeNew',
            'email' : 'janedoe@example.com',
            'password' : 'Password1234',
            'password_confirm' : 'Password1234' }

    """
    Test cases
    """

    def test_update_admin_url(self):
        self.assertEqual(self.url, '/administrator-accounts/update/admin@example.com/')
    
    def test_view_restricted_for_guest(self):
        # Guest should be on the log in page only
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_login(response=response)

    def test_view_restricted_for_student(self):
        # Create and log in as student
        self._create_student_user()
        self._log_in_as_student()

        # Student should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)

        # Check dashboard used
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.STUDENT)

    def test_view_restricted_for_teacher(self):
        # Create and log in as teacher
        self._create_teacher_user()
        self._log_in_as_teacher()

        # Teacher should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)

        # Check dashboard used
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.TEACHER)

    def test_view_restricted_for_admin(self):
        # Create and log in as admin
        self._log_in_as_admin()

        # Admin should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)

        # Check dashboard used
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.ADMIN)

    def test_view_allowed_for_director(self):
        # Log in as director 
        self._log_in_as_director()

        # Director should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/admin/update_admin.html')

    def test_update_of_non_existent_user(self):
        # Log in as director
        self._log_in_as_director()

        before_user_count = User.objects.count()
        before_admin_profile_count = AdminProfile.objects.count()
        url = reverse('update_admin', kwargs={ 'email': 'invalid@example.com'})
        response = self.client.post(url, self.form_input, follow=True)
        after_user_count = User.objects.count()
        after_admin_profile_count = AdminProfile.objects.count()

        # Check no deletes have taken place
        self.assertEqual(before_admin_profile_count, after_admin_profile_count)
        self.assertEqual(before_user_count, after_user_count)

        # Should redirect to view admin accounts page
        response_url = reverse('view_admins')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'templates/admin/view_admins.html')

        # Should be error message on it
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.ERROR)

    def test_successful_update_of_valid_user(self):
        # Log in as director
        self._log_in_as_director()

        before_user_count = User.objects.count()
        before_admin_profile_count = AdminProfile.objects.count()
        url = reverse('update_admin', kwargs={ 'email': 'admin@example.com'})
        response = self.client.post(url, self.form_input, follow=True)
        after_user_count = User.objects.count()
        after_admin_profile_count = AdminProfile.objects.count()

        # Check no deletes have taken place
        self.assertEqual(before_admin_profile_count, after_admin_profile_count)
        self.assertEqual(before_user_count, after_user_count)

        # Should redirect to view admin accounts page
        response_url = reverse('view_admins')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'templates/admin/view_admins.html')

        # Should be success message on it
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.SUCCESS)

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username = 'admin@example.com')

        user = User.objects.get(username = 'janedoe@example.com')
        self.assertEqual(user.first_name, 'JaneNew')
        self.assertEqual(user.last_name, 'DoeNew')
        self.assertEqual(user.email, 'janedoe@example.com')
        self.assertEqual(user.type, UserType.ADMIN)
        self.assertEqual(user.is_active, True)

        # Password remains unchanged
        is_password_correct = check_password('Password1234', user.password)
        self.assertTrue(is_password_correct)

    def test_unsuccessful_update_of_valid_user(self):
        self.form_input['email'] = 'director@example.com' # Pre-existing email - should fail clean()
        self._log_in_as_director()

        before_user_count = User.objects.count()
        before_admin_profile_count = AdminProfile.objects.count()
        url = reverse('update_admin', kwargs={ 'email': 'admin@example.com'})
        response = self.client.post(url, self.form_input, follow=True)
        after_user_count = User.objects.count()
        after_admin_profile_count = AdminProfile.objects.count()

        # Check no deletes have taken place
        self.assertEqual(before_admin_profile_count, after_admin_profile_count)
        self.assertEqual(before_user_count, after_user_count)

        # Should rerender same page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'templates/admin/update_admin.html')

        # User should be unchanged
        user = User.objects.get(username = 'admin@example.com')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'admin@example.com')
        self.assertEqual(user.type, UserType.ADMIN)
        self.assertEqual(user.is_active, True)

        # Password remains unchanged
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
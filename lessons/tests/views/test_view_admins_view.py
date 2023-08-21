
from django.test import TestCase
from lessons.models.user_models import UserType
from lessons.forms.user_forms import *
from django import forms
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from ..helpers import LoginHelper

class ViewAdminsViewTestCase(TestCase, LoginHelper):
    """
    Contains test cases for the view_admin_accounts view
    """
    def setUp(self):
        self.url = reverse('view_admins')

        self._create_student_user()
        self._create_admin_user()
        self._create_director_user()

    """
    Test cases
    """

    def test_view_admin_accounts_url(self):
        self.assertEqual(self.url, '/administrator-accounts/')
    
    def test_get_view_admin_accounts_as_guest_restricted(self):
        response = self.client.get(self.url, follow=True)

        # Guest aren't logged in
        self.assertFalse(self._is_logged_in())

        self.assert_redirected_to_login(response=response)

    def test_get_view_admin_accounts_as_student_restricted(self):
        self._log_in_as_student()
        response = self.client.get(self.url, follow=True)

        # Check login success
        self.assertTrue(self._is_logged_in())

        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.STUDENT)
    
    def test_get_view_admin_accounts_as_admin_restricted(self):
        self._log_in_as_admin()
        response = self.client.get(self.url, follow=True)

        # Check login success
        self.assertTrue(self._is_logged_in())

        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.ADMIN)

    def test_get_view_admin_accounts_as_director(self):
        self._log_in_as_director()
        response = self.client.get(self.url, follow=True)

        # Check login success
        self.assertTrue(self._is_logged_in())

        # Check for redirect back
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/admin/view_admins.html')


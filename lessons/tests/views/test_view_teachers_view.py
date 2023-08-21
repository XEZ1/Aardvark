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
        self.url = reverse('view_teachers')

        # Create users -> teacher, admin, director
        self._create_teacher_user()
        self._create_admin_user()
        self._create_director_user()

    """
    Test cases
    """

    def test_view_teacher_accounts_url(self):
        self.assertEqual(self.url, '/teachers/')

    def test_get_view_teacher_accounts_as_guest_restricted(self):
        
        response = self.client.get(self.url, follow=True)

        # Guest aren't logged in
        self.assertFalse(self._is_logged_in())

        self.assert_redirected_to_login(response=response)

    def test_get_view_teacher_accounts_as_student_restricted(self):

        # Create and log in as student user
        self._create_student_user()
        self._log_in_as_student()
        response = self.client.get(self.url, follow=True)

        # Check login success
        self.assertTrue(self._is_logged_in())

        # Student is redirected to the dashboard
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.STUDENT)

    def test_get_view_teacher_accounts_as_teacher_restricted(self):

        # Log in as a teacher
        self._log_in_as_teacher()
        response = self.client.get(self.url, follow=True)
        
        # Check login success
        self.assertTrue(self._is_logged_in())

        # Check template used
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.TEACHER)

    def test_get_view_teacher_accounts_as_director(self):
       
        # Log in as a director
        self._log_in_as_director()
        response = self.client.get(self.url, follow=True)

        # Check login success
        self.assertTrue(self._is_logged_in())

        # Check for redirect back
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/teacher/view_teachers.html')

    
from django.test import TestCase
from lessons.models.user_models import UserType
from django.urls import reverse
from ..helpers import LoginHelper
from django.contrib import messages

class ViewStudentsViewTestCase(TestCase, LoginHelper):
    """
    Contains test cases for the view_students view
    """
    def setUp(self):
        self.url = reverse('view_students')

        self._create_student_user()
        self._create_secondary_student_user()
        self._create_admin_user()
        self._create_director_user()

    """
    Test cases
    """

    def test_view_students_url(self):
        self.assertEqual(self.url, '/students/')

    def test_get_view_students_as_guest_restricted(self):
        response = self.client.get(self.url, follow=True)

        # Guest aren't logged in
        self.assertFalse(self._is_logged_in())

        self.assert_redirected_to_login(response=response)

    def test_get_view_students_as_student_restricted(self):
        self._log_in_as_student()
        response = self.client.get(self.url, follow=True)

        # Check login success
        self.assertTrue(self._is_logged_in())

        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.STUDENT)

    def test_get_view_students_as_teacher_restricted(self):
        self._create_teacher_user()
        self._log_in_as_teacher()
        response = self.client.get(self.url, follow=True)

        # Check login success
        self.assertTrue(self._is_logged_in())

        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.TEACHER)

    def test_get_view_students_as_admin(self):
        self._log_in_as_admin()
        response = self.client.get(self.url, follow=True)

        # Check login success
        self.assertTrue(self._is_logged_in())

        # Check for redirect back
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/student/view_students.html')

    def test_get_view_students_as_director(self):
        self._log_in_as_director()
        response = self.client.get(self.url, follow=True)

        # Check login success
        self.assertTrue(self._is_logged_in())

        # Check for redirect back
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/student/view_students.html')

    def test_empty_search_returns_all_requests(self):
        self._log_in_as_admin()

        response = self.client.get(self.url, search_term = '')

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # No message should appear for empty search
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 0)

        # Should only be two students displayed
        students_displayed = response.context['students']
        self.assertEqual(len(students_displayed), 2)

    def test_search_is_not_case_sensitive(self):
        self._log_in_as_admin()

        search_data = { "search_term": "JANE DOE" }
        response = self.client.get(self.url, search_data, follow=True)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Info message should appear
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.INFO)

        # Should display 1 student
        students_displayed = response.context['students']
        self.assertEqual(len(students_displayed), 1)

    def test_search_checks_email(self):
        self._log_in_as_admin()

        search_data = { "search_term": "student_2@example.com" }
        response = self.client.get(self.url, search_data, follow=True)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Info message should appear
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.INFO)

        # Should display 1 student
        students_displayed = response.context['students']
        self.assertEqual(len(students_displayed), 1)

    def test_search_checks_full_name(self):
        self._log_in_as_admin()

        search_data = { "search_term": "John Doe" }
        response = self.client.get(self.url, search_data, follow=True)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Info message should appear
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.INFO)

        # Should display 1 student
        students_displayed = response.context['students']
        self.assertEqual(len(students_displayed), 1)
        self.assertEqual(students_displayed[0].user, self.student_user_2)

    def test_search_with_no_results(self):
        self._log_in_as_admin()

        search_data = { "search_term": "No match john doe" }
        response = self.client.get(self.url, search_data, follow=True)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Error message should appear
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.ERROR)

        # Should display 0 student
        students_displayed = response.context['students']
        self.assertEqual(len(students_displayed), 0)

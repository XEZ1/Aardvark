from django.test import TestCase
from lessons.forms.user_forms import *
from django.urls import reverse
from ..helpers import *
from django.contrib import messages

class ViewAllTransactionsViewTestCase(TestCase, LoginHelper, LessonHelper, SchoolTermHelper, TransferHelper):
    """
    Contains the test cases for the view all transactions view
    """

    def setUp(self):
        """
        Get routed URL
        """

        self._create_student_user()
        self._create_admin_user()
        self._create_teacher_user()
        self._create_secondary_student_user()
        self._create_school_term()
        self._assign_lesson_request_to_user(self.student_user)
        self._assign_lesson_booking_to_lesson_request(self.student_user.student_profile.lesson_requests.first())
        self.lesson_booking = self.admin_user.admin_profile.lesson_bookings.first()
        self._create_transfer(self.lesson_booking)
        self._assign_lesson_request_to_user(self.student_user_2)
        self._assign_lesson_booking_to_lesson_request(self.student_user_2.student_profile.lesson_requests.first())
        self.lesson_booking = self.admin_user.admin_profile.lesson_bookings.last()
        self._create_transfer(self.lesson_booking)

        # It is done this way so that if URL it altered in future, test doesn't break
        self.url = reverse('view_all_transactions')

    """
    Test cases
    """

    def test_register_transactions_url(self):
        self.assertEqual(self.url, '/transactions/')

    def test_view_restricted_for_guest(self):
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_login(response)

    def test_get_all_transactions_for_admin(self):
        self._log_in_as_admin()

        # Admin should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Should be displayed two invoices and two transactions
        transfers_displayed = response.context['transactions']
        self.assertEqual(len(transfers_displayed), 4)

        # Check template used - should be simple one
        self.assertTemplateUsed(response, 'templates/transfer/view_transactions.html')

    def test_get_all_transactions_for_director(self):
        self._create_director_user()
        self._log_in_as_director()

        # Director should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Should be displayed two invoices and two transactions
        transfers_displayed = response.context['transactions']
        self.assertEqual(len(transfers_displayed), 4)

        # Check template used - should be simple one
        self.assertTemplateUsed(response, 'templates/transfer/view_transactions.html')

    def test_view_restricted_for_student(self):
        self._log_in_as_student()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.STUDENT)

    def test_view_restricted_for_teacher(self):
        self._log_in_as_teacher()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.TEACHER)

from django.test import TestCase
from lessons.forms.user_forms import *
from django.urls import reverse
from ..helpers import *
from django.contrib import messages

class ViewTransactionsViewTestCase(TestCase, LoginHelper, LessonHelper, SchoolTermHelper, TransferHelper):
    """
    Contains the test cases for the view transactions view
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

        # It is done this way so that if URL it altered in future, test doesn't break
        self.url = reverse('view_transactions', kwargs={ 'email': self.student_user.email })

    """
    Test cases
    """

    def test_register_transactions_url(self):
        self.assertEqual(self.url, f'/transactions/{ self.student_user.email }/')

    def test_view_restricted_for_guest(self):
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_login(response)

    def test_get_all_transactions_for_student(self):
        self._log_in_as_student()

        # Student should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Should be displayed one invoice and one transaction
        transfers_displayed = response.context['transactions']
        self.assertEqual(len(transfers_displayed), 2)

        # Check template used - should be simple one
        self.assertTemplateUsed(response, 'templates/transfer/view_transactions.html')

    def test_get_all_transactions_for_admin(self):
        self._log_in_as_admin()

        # Admin should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Should be displayed one invoice and one transaction
        transfers_displayed = response.context['transactions']
        self.assertEqual(len(transfers_displayed), 2)

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

        # Should be displayed one invoice and one transaction
        transfers_displayed = response.context['transactions']
        self.assertEqual(len(transfers_displayed), 2)

        # Check template used - should be simple one
        self.assertTemplateUsed(response, 'templates/transfer/view_transactions.html')


    def test_view_restricted_for_teacher(self):
        self._log_in_as_teacher()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.TEACHER)

    def test_day_balance_is_calculated_live(self):
        self._log_in_as_student()

        # Student should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Should display booking fee (negative)
        transfers_displayed = response.context['transactions']
        self.assertEqual(transfers_displayed[1].fee, -10)
        # Should display transfer amount
        transfers_displayed = response.context['transactions']
        self.assertEqual(transfers_displayed[0].fee, 250)
        # Should display difference between fee and transfer amount
        transfers_displayed = response.context['transactions']
        self.assertEqual(transfers_displayed[0].balance, 240)

        # Check template used - should be simple one
        self.assertTemplateUsed(response, 'templates/transfer/view_transactions.html')

    def test_get_right_booking_invoice(self):
        self._log_in_as_student()

        # Student should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Should display "Payment" for transfers
        transfers_displayed = response.context['transactions']
        self.assertEqual(transfers_displayed[0].reference, "Payment")
        # Should display the right invoice for the booking
        transfers_displayed = response.context['transactions']
        self.assertEqual(transfers_displayed[1].reference, self.lesson_booking.invoice_number())

        # Check template used - should be simple one
        self.assertTemplateUsed(response, 'templates/transfer/view_transactions.html')

from django.test import TestCase
from lessons.models.user_models import UserType
from django.urls import reverse
from datetime import timedelta
from ..helpers import *

class RegisterTransferViewTestCase(TestCase, LoginHelper, LessonHelper, SchoolTermHelper, TransferHelper):
    """
    Contains the test cases for the school transfer registration view
    """

    def setUp(self):
        """
        Simulate the form input and get routed URL
        """

        self._create_student_user()
        self._create_admin_user()
        self._create_school_term()
        self._create_teacher_user()
        self._assign_lesson_request_to_user(self.student_user)
        self.lesson_request = self.student_user.student_profile.lesson_requests.first()
        self._assign_lesson_booking_to_lesson_request(self.lesson_request)
        self.lesson_booking = self.admin_user.admin_profile.lesson_bookings.first()

        self.url = reverse('register_transfer')

        self.form_input = {
            'date': '2022-01-01',#yyyy-mm-dd
            'balance' : 250,
            'invoice_ref_no': self.lesson_booking.invoice_number()
        }

    """
    Test cases
    """

    def test_register_transfer_url(self):
        self.assertEqual(self.url, '/register-transfer/')

    def test_get_register_for_director(self):
        self._create_director_user()
        self._log_in_as_director()

        # Director should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/transfer/register_transfer.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RegisterTransferForm))

        # Shouldn't be bound as new instance
        self.assertFalse(form.is_bound)

    def test_get_register_for_admin(self):
        self._log_in_as_admin()

        # Director should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/transfer/register_transfer.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RegisterTransferForm))

        # Shouldn't be bound as new instance
        self.assertFalse(form.is_bound)

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

    def test_view_restricted_for_guest(self):
        response = self.client.get(self.url, follow=True)

        # Check template used
        self.assertTemplateUsed(response, 'templates/log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LoginUserForm))

        # Shouldn't be bound as new instance
        self.assertFalse(form.is_bound)

    def test_unsuccesful_transfer_registration(self):
        self._log_in_as_admin()
        self.assertTrue(self._is_logged_in())

        self.form_input['invoice_ref_no'] = '9999-999'

        before_count = Transfer.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Transfer.objects.count()

        # Check no inserts have taken place
        self.assertEqual(before_count, after_count)

        # Check page still valid
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'templates/transfer/register_transfer.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RegisterTransferForm))
        self.assertTrue(form.is_bound)

    def test_successful_transfer_registration(self):
        self._log_in_as_admin()
        self.assertTrue(self._is_logged_in())

        before_count = Transfer.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Transfer.objects.count()
        self.assertEqual(before_count, after_count - 1)

        # Check that response is correct
        self.assertRedirects(response, reverse("register_transfer"), status_code=302, target_status_code=200)

        # Check that the fields went through to database
        trans = Transfer.objects.get(date = '2022-01-01')
        self.assertEqual(trans.date.strftime("%Y-%m-%d"), '2022-01-01')
        self.assertEqual(trans.balance, 250)
        self.assertEqual(trans.lesson_booking.id, self.lesson_booking.id)

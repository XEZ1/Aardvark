from django.test import TestCase
from lessons.forms.user_forms import *
from django.urls import reverse
from ..helpers import *
from django.contrib import messages

class ViewInvoiceViewTestCase(TestCase, LoginHelper, LessonHelper, SchoolTermHelper, TransferHelper):
    """
    Contains the test cases for the view invoice view
    """

    def setUp(self):
        """
        Get routed URL
        """

        self._create_student_user()
        self._create_admin_user()
        self._create_teacher_user()
        self._create_school_term()
        self._assign_lesson_request_to_user(self.student_user)
        self._assign_lesson_booking_to_lesson_request(self.student_user.student_profile.lesson_requests.first())
        self.lesson_booking = self.admin_user.admin_profile.lesson_bookings.first()

        # It is done this way so that if URL it altered in future, test doesn't break
        self.url = reverse('view_invoice_for_lesson_booking', kwargs={ 'id': self.lesson_booking.id })

    """
    Test cases
    """
    def test_view_url(self):
        self.assertEqual(self.url, f'/lesson-bookings/invoice/{self.lesson_booking.id}/')

    def test_view_restricted_for_guest(self):
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_login(response=response)

    def test_view_restricted_for_teacher(self):
        self._log_in_as_teacher()
        self.assertTrue(self._is_logged_in())
        
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.TEACHER)

    def test_get_invoice_as_student(self):
        self._log_in_as_student()
        response = self.client.get(self.url, follow=True)
        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)
        # Check template used
        self.assertTemplateUsed(response, 'templates/lesson/lesson_booking_invoice.html')

        # Ensure that it is the correct invoice
        self.assertContains(response, f'<p class="float-end"><b>Reference No: </b>{ self.lesson_booking.invoice_number() }</p>', status_code=200)

    def test_get_invoice_as_admin(self):
        self._log_in_as_admin()
        response = self.client.get(self.url, follow=True)
        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)
        # Check template used
        self.assertTemplateUsed(response, 'templates/lesson/lesson_booking_invoice.html')

        # Ensure that it is the correct invoice
        self.assertContains(response, f'<p class="float-end"><b>Reference No: </b>{ self.lesson_booking.invoice_number() }</p>', status_code=200)

    def test_get_invoice_that_does_not_exist(self):
        self._log_in_as_admin()
        url = reverse('view_invoice_for_lesson_booking', kwargs={ 'id': 100 })
        response = self.client.get(url, follow=True)

        # Should redirect to view page
        response_url = reverse('view_lesson_bookings')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        # Should be error message on it
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.ERROR)
    
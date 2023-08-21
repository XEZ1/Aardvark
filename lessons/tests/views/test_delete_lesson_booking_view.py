from django.test import TestCase
from lessons.models.user_models import UserType
from lessons.forms.user_forms import *
from lessons.models.lesson_models import *
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from lessons.tests.helpers import LoginHelper, LessonHelper, SchoolTermHelper
from django.contrib import messages

class DeleteLessonBookingViewTestCase(TestCase, LoginHelper, LessonHelper, SchoolTermHelper):
    """
    Contains the test cases for the delete lesson booking view
    """

    def setUp(self):
        """
        Generate lesson booking that will be deleted.
        """
        self._create_student_user()
        self._create_admin_user()
        self._create_school_term()
        self._create_teacher_user()
        self._assign_lesson_request_to_user(self.student_user)
        self.lesson_request = self.student_user.student_profile.lesson_requests.first()
        self._assign_lesson_booking_to_lesson_request(self.lesson_request)
        self.lesson_booking = self.lesson_request.lesson_booking

        self.url = reverse('delete_lesson_booking', kwargs={ 'id': self.lesson_booking.id })

    """
    Test cases
    """

    def test_url(self):
        self.assertEqual(self.url, f'/lesson-bookings/delete/{ self.lesson_booking.id }/')

    def test_view_restricted_for_guest(self):
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_login(response=response)

    def test_view_restricted_for_student(self):
        self._log_in_as_student()
        self.assertTrue(self._is_logged_in())
        
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.STUDENT)

    def test_view_available_for_director(self):
        self._create_director_user()
        self._log_in_as_director()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/lesson/delete_lesson_booking.html')

    def test_view_available_for_admin(self):
        self._log_in_as_admin()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/lesson/delete_lesson_booking.html')

    def test_delete_of_non_existent_lesson_booking(self):
        self._log_in_as_admin()

        before_count = LessonBooking.objects.count()
        url = reverse('delete_lesson_booking', kwargs={ 'id': 2 })
        response = self.client.post(url, follow=True)
        after_count = LessonBooking.objects.count()

        # Check no deletes have taken place
        self.assertEqual(before_count, after_count)

        # Should redirect to view page
        response_url = reverse('view_lesson_bookings')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        # Should be error message on it
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.ERROR)

    def test_successful_delete_of_valid_lesson_request(self):
        self._log_in_as_admin()

        before_count = LessonBooking.objects.count()
        url = reverse('delete_lesson_booking', kwargs={ 'id': self.lesson_booking.id })
        response = self.client.post(url, follow=True)
        after_count = LessonBooking.objects.count()

        # Check deletes have taken place
        self.assertEqual(before_count, after_count + 1)

        # Should redirect
        response_url = reverse('view_lesson_bookings')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        # Should be success message on it
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.SUCCESS)

        self.assertFalse(LessonBooking.objects.filter(pk=self.lesson_booking.id).exists())
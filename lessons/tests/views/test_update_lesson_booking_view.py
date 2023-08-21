from django.test import TestCase
from lessons.models.user_models import UserType
from lessons.forms.user_forms import *
from django.urls import reverse
from ..helpers import LoginHelper, LessonHelper, SchoolTermHelper
from lessons.models.lesson_models import AvailabilityPeriod
from django.contrib import messages
from datetime import datetime, timedelta
from lessons.models.lesson_models import *

class UpdateLessonBookingViewTestCase(TestCase, LoginHelper, LessonHelper, SchoolTermHelper):
    """
    Contains the test cases for the update lesson booking view
    """

    def setUp(self):
        """
        Simulate the form input
        """
        self._create_student_user()
        self._create_teacher_user()
        self._create_secondary_teacher_user()
        self._create_school_term()
        self._assign_lesson_request_to_user(self.student_user)
        self._create_admin_user()
        self._assign_lesson_booking_to_lesson_request(self.student_user.student_profile.lesson_requests.first())

        self.lesson_booking = self.admin_user.admin_profile.lesson_bookings.first()
        self.time = self.lesson_booking.regular_start_time
        self.date = datetime.now().date() + timedelta(days=1)
        self.form_input = {
            'school_term': self.school_term.id,
            'start_date': self.date.strftime("%Y-%m-%d"),
            'end_date': (self.date + timedelta(days=30)).strftime("%Y-%m-%d"),
            'teacher': self.teacher_user_2.teacher_profile.id, 
            'regular_day': AvailabilityPeriod.TUESDAY,
            'regular_start_time': self.time,
            'interval': '2',
            'duration': '45',
            'quantity': '1', 
            }

        self.url = reverse('update_lesson_booking', kwargs={ 'id': self.lesson_booking.id })

    """
    Test cases
    """

    def test_url(self):
        self.assertEqual(self.url, f'/lesson-bookings/update/{ self.lesson_booking.id }/')
    
    def test_view_restricted_for_guest(self):
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_login(response=response)

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

    def test_view_available_for_director(self):
        self._create_director_user()
        self._log_in_as_director()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/lesson/update_lesson_booking.html')

    def test_view_available_for_admin(self):
        self._log_in_as_admin()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/lesson/update_lesson_booking.html')

    def test_update_of_non_existent_lesson_booking(self):
        self._log_in_as_admin()

        before_count = LessonBooking.objects.count()
        url = reverse('update_lesson_booking', kwargs={ 'id': 2 })
        response = self.client.post(url, self.form_input, follow=True)
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

    def test_successful_update_of_valid_lesson_booking(self):
        self._log_in_as_admin()

        before_count = LessonBooking.objects.count()
        url = reverse('update_lesson_booking', kwargs={ 'id': self.lesson_booking.id })
        response = self.client.post(url, self.form_input, follow=True)
        after_count = LessonBooking.objects.count()

        # Check no deletes have taken place
        self.assertEqual(before_count, after_count)

        # Should redirect
        response_url = reverse('view_lesson_bookings')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        # Should be success message on it
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.SUCCESS)

        self.lesson_booking = LessonBooking.objects.get(pk=self.lesson_booking.id)

        self.assertEqual(self.lesson_booking.start_date.strftime("%Y-%m-%d"), self.date.strftime("%Y-%m-%d")) 
        self.assertEqual(self.lesson_booking.end_date.strftime("%Y-%m-%d"), 
            (self.date + timedelta(days=30)).strftime("%Y-%m-%d")) 
        self.assertEqual(self.lesson_booking.school_term, self.school_term) 
        self.assertEqual(self.lesson_booking.duration, 45)
        self.assertEqual(self.lesson_booking.interval, 2)
        self.assertEqual(self.lesson_booking.quantity, 1)
        self.assertEqual(self.lesson_booking.teacher, self.teacher_user_2.teacher_profile)
        self.assertEqual(self.lesson_booking.regular_day, AvailabilityPeriod.TUESDAY) 
        self.assertEqual(self.lesson_booking.regular_start_time, self.time) 
        self.assertEqual(self.lesson_booking.admin_profile, self.admin_user.admin_profile) 

    def test_unsuccessful_update_of_valid_lesson_booking(self):
        self.form_input['regular_day'] = '' # Should cause error
        self._log_in_as_admin()

        before_count = LessonBooking.objects.count()
        url = reverse('update_lesson_booking', kwargs={ 'id': self.lesson_booking.id })
        response = self.client.post(url, self.form_input, follow=True)
        after_count = LessonBooking.objects.count()

        # Check no deletes have taken place
        self.assertEqual(before_count, after_count)

        # Should rerender same page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'templates/lesson/update_lesson_booking.html')

        # Model should be unchanged
        lesson_booking = LessonBooking.objects.get(pk=self.lesson_booking.id)

        self.assertEqual(lesson_booking.school_term, self.school_term)
        self.assertEqual(lesson_booking.start_date.strftime("%Y-%m-%d"), (self.date - timedelta(days=1)).strftime("%Y-%m-%d")) 
        self.assertEqual(lesson_booking.end_date.strftime("%Y-%m-%d"), (self.date + timedelta(days=29)).strftime("%Y-%m-%d")) 
        self.assertEqual(lesson_booking.duration, 60)
        self.assertEqual(lesson_booking.interval, 1)
        self.assertEqual(lesson_booking.quantity, 2)
        self.assertEqual(lesson_booking.teacher.id, self.teacher_user.teacher_profile.id)
        self.assertEqual(lesson_booking.regular_day, AvailabilityPeriod.MONDAY) 
        self.assertEqual(lesson_booking.regular_start_time, self.time) 
        self.assertEqual(lesson_booking.lesson_request, self.lesson_booking.lesson_request) 
        self.assertEqual(lesson_booking.admin_profile, self.admin_user.admin_profile) 
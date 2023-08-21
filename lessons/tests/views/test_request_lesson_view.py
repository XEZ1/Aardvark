from django.test import TestCase
from lessons.models.user_models import UserType
from lessons.models.lesson_models import AvailabilityPeriod, LessonRequest
from lessons.forms.lesson_forms import RequestLessonForm
from django.urls import reverse
from ..helpers import LoginHelper, SchoolTermHelper, LessonHelper
from django.contrib import messages

class RequestLessonViewTestCase(TestCase, LoginHelper, SchoolTermHelper, LessonHelper):
    """
    Contains the test cases for the request lesson view
    """

    def setUp(self):
        """
        Simulate the form input and get routed URL
        """

        # It is done this way so that if URL it altered in future, test doesn't break
        self.url = reverse('request_lesson')
        self._create_student_user()
        self.form_input = {
            'interval': '1',
            'duration': '60',
            'quantity': '2',
            'notes': 'Please can I have example teacher',
            'availability': [AvailabilityPeriod.MONDAY, AvailabilityPeriod.TUESDAY],
            'recipient_profile_id': self.student_user.student_profile.id
            }

    """
    Test cases
    """

    def test_request_lesson_url(self):
        self.assertEqual(self.url, '/request-lesson/')

    def test_view_restricted_for_guest(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_login(response)

    def test_view_restricted_for_admin(self):
        self._create_admin_user()
        self._log_in_as_admin()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response, dashboard_type=UserType.ADMIN)

    def test_view_restricted_for_director(self):
        self._create_director_user()
        self._log_in_as_director()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response, dashboard_type=UserType.DIRECTOR)

    def test_view_allowed_for_student(self):
        self._log_in_as_student()
        self.assertTrue(self._is_logged_in())

        # Student should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/lesson/request_lesson.html')

    def test_unsuccesful_lesson_request(self):
        self._log_in_as_student()
        self.assertTrue(self._is_logged_in())

        self.form_input['availability'] = ''

        before_count = LessonRequest.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = LessonRequest.objects.count()

        # Check no inserts have taken place
        self.assertEqual(before_count, after_count)

        # Check page still valid
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'templates/lesson/request_lesson.html')

        form = response.context['form']
        self.assertTrue(isinstance(form, RequestLessonForm))
        self.assertTrue(form.is_bound)

        # An error message should've flagged.
        self.assertTrue(len(form.errors) >= 1)

    def test_succesful_lesson_request(self):
        self._log_in_as_student()
        self.assertTrue(self._is_logged_in())

        before_count = LessonRequest.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = LessonRequest.objects.count()

        # Check insert has taken place
        self.assertEqual(before_count, after_count - 1)
        
        # Check that redirect is to view lesson requests view
        response_url = reverse('view_lesson_requests')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        # Check that response goes to correct dashboard
        self.assertTemplateUsed(response, 'templates/lesson/view_lesson_requests.html')

        # A success message should've flagged.
        messagesList = list(response.context['messages'])
        self.assertTrue(len(messagesList) >= 1)
        self.assertEqual(messagesList[0].level, messages.SUCCESS)

        # Check that the fields went through to database
        lesson_request = self.student_user.student_profile.lesson_requests.first()

        self.assertEqual(lesson_request.duration, 60)
        self.assertEqual(lesson_request.interval, 1)
        self.assertEqual(lesson_request.quantity, 2)
        self.assertEqual(lesson_request.notes, 'Please can I have example teacher')
        self.assertEqual(lesson_request.availability, 'MONDAY,TUESDAY') # Cleans data correctly
        self.assertEqual(lesson_request.student_profile, self.student_user.student_profile)

    def test_succesful_repeat_lesson_request(self):
        self._create_teacher_user()
        self._create_school_term()
        self._assign_lesson_request_to_user(self.student_user)
        self._create_admin_user()
        self._assign_lesson_booking_to_lesson_request(self.student_user.student_profile.lesson_requests.first())

        self.lesson_booking = self.admin_user.admin_profile.lesson_bookings.first()

        # Check URL
        url = reverse('request_repeat_booking', kwargs={ 'id': self.lesson_booking.id })
        self.assertEqual(url, f'/lesson-bookings/repeat/{self.lesson_booking.id}/')

        self._log_in_as_student()
        self.assertTrue(self._is_logged_in())

        # Check that fields have populated correctly as last repeat
        response_get = self.client.get(url)
        form = response_get.context['form']
        self.assertEqual(form['duration'].initial, 60)
        self.assertEqual(form['interval'].initial, 1)
        self.assertEqual(form['quantity'].initial, 2)
        self.assertEqual(form['notes'].initial, 'Test notes')
        self.assertEqual(form['recipient_profile_id'].initial, self.lesson_booking.lesson_request.student_profile.id)
        self.assertEqual(form['availability'].initial, self.lesson_booking.lesson_request.availability_formatted_as_list())

        before_count = LessonRequest.objects.count()
        response = self.client.post(url, self.form_input, follow=True)
        after_count = LessonRequest.objects.count()

        # Check insert has taken place
        self.assertEqual(before_count, after_count - 1)
        
        # Check that redirect is to view lesson requests view
        response_url = reverse('view_lesson_requests')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        # Check that response goes to correct dashboard
        self.assertTemplateUsed(response, 'templates/lesson/view_lesson_requests.html')

        # A success message should've flagged.
        messagesList = list(response.context['messages'])
        self.assertTrue(len(messagesList) >= 1)
        self.assertEqual(messagesList[0].level, messages.SUCCESS)

        # Check that the fields went through to database
        lesson_request = list(self.student_user.student_profile.lesson_requests.all())[0]

        self.assertEqual(lesson_request.duration, 60)
        self.assertEqual(lesson_request.interval, 1)
        self.assertEqual(lesson_request.quantity, 2)
        self.assertEqual(lesson_request.notes, 'Test notes')
        self.assertEqual(lesson_request.availability, 'MONDAY,TUESDAY') # Cleans data correctly
        self.assertEqual(lesson_request.student_profile, self.student_user.student_profile)

    def test_succesful_repeat_lesson_request_for_non_repeat_lesson(self):
        self._create_teacher_user()
        self._create_school_term()
        self._assign_lesson_request_to_user(self.student_user)

        # Check URL
        url = reverse('request_repeat_booking', kwargs={ 'id': 100 })
        self.assertEqual(url, f'/lesson-bookings/repeat/{100}/')

        self._log_in_as_student()
        self.assertTrue(self._is_logged_in())

        before_count = LessonRequest.objects.count()
        response = self.client.post(url, self.form_input, follow=True)
        after_count = LessonRequest.objects.count()

         # Should redirect to view page
        response_url = reverse('view_lesson_bookings')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        # Should be error message on it
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.ERROR)
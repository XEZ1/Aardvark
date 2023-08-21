from django.test import TestCase
from lessons.models.user_models import UserType
from lessons.forms.user_forms import *
from django.urls import reverse
from ..helpers import LoginHelper, LessonHelper
from lessons.models.lesson_models import AvailabilityPeriod
from django.contrib import messages
from datetime import datetime
from lessons.models.lesson_models import *

class UpdateLessonRequestViewTestCase(TestCase, LoginHelper, LessonHelper):
    """
    Contains the test cases for the update lesson request view
    """

    def setUp(self):
        """
        Simulate the form input on view
        """
        
        self.time = datetime.now().time()
        self._create_student_user()
        self._assign_lesson_request_to_user(self.student_user)

        self.lesson_request = self.student_user.student_profile.lesson_requests.first()
        self.form_input = {
            'interval': '2',
            'duration': '45',
            'quantity': '3',
            'notes': 'Please can I have example teacher 2',
            'availability': [AvailabilityPeriod.TUESDAY] }

        self.url = reverse('update_lesson_request', kwargs={ 'id': self.lesson_request.id })

    """
    Test cases
    """

    def test_update_admin_url(self):
        self.assertEqual(self.url, f'/lesson-requests/update/{ self.lesson_request.id }/')
    
    def test_view_restricted_for_guest(self):
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_login(response=response)

    def test_view_restricted_for_director(self):
        self._create_director_user()
        self._log_in_as_director()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.DIRECTOR)

    def test_view_restricted_for_admin(self):
        self._create_admin_user()
        self._log_in_as_admin()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.ADMIN)

    def test_view_allowed_for_student(self):
        self._log_in_as_student()

        # User should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/lesson/update_lesson_request.html')

    def test_update_of_non_existent_lesson_request(self):
        self._log_in_as_student()

        before_count = LessonRequest.objects.count()
        url = reverse('update_lesson_request', kwargs={ 'id': 2 })
        response = self.client.post(url, self.form_input, follow=True)
        after_count = LessonRequest.objects.count()

        # Check no deletes have taken place
        self.assertEqual(before_count, after_count)

        # Should redirect to view page
        response_url = reverse('view_lesson_requests')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        # Should be error message on it
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.ERROR)

    def test_successful_update_of_valid_lesson_request(self):
        self._log_in_as_student()

        before_count = LessonRequest.objects.count()
        url = reverse('update_lesson_request', kwargs={ 'id': self.lesson_request.id })
        response = self.client.post(url, self.form_input, follow=True)
        after_count = LessonRequest.objects.count()

        # Check no deletes have taken place
        self.assertEqual(before_count, after_count)

        # Should redirect
        response_url = reverse('view_lesson_requests')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        # Should be success message on it
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.SUCCESS)

        lesson_request = LessonRequest.objects.get(pk=self.lesson_request.id)

        self.assertEqual(lesson_request.duration, 45)
        self.assertEqual(lesson_request.interval, 2)
        self.assertEqual(lesson_request.quantity, 3)
        self.assertEqual(lesson_request.notes, 'Please can I have example teacher 2')
        self.assertEqual(lesson_request.availability, 'TUESDAY') # Cleans data correctly

    def test_unsuccessful_update_of_valid_lesson_request(self):
        self.form_input['availability'] = '' # Should cause error
        self._log_in_as_student()

        before_count = LessonRequest.objects.count()
        url = reverse('update_lesson_request', kwargs={ 'id': self.lesson_request.id })
        response = self.client.post(url, self.form_input, follow=True)
        after_count = LessonRequest.objects.count()

        # Check no deletes have taken place
        self.assertEqual(before_count, after_count)

        # Should rerender same page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'templates/lesson/update_lesson_request.html')

        # Model should be unchanged
        lesson_request = LessonRequest.objects.get(pk=self.lesson_request.id)
        self.assertEqual(lesson_request.duration, 60)
        self.assertEqual(lesson_request.interval, 1)
        self.assertEqual(lesson_request.quantity, 2)
        self.assertEqual(lesson_request.notes, 'Test notes')
        self.assertEqual(lesson_request.availability, 'MONDAY,TUESDAY')
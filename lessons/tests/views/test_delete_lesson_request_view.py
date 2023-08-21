from django.test import TestCase
from lessons.models.user_models import UserType
from lessons.forms.user_forms import *
from lessons.models.lesson_models import *
from django.urls import reverse
from ..helpers import LoginHelper, LessonHelper
from django.contrib import messages

class DeleteLessonRequestViewTestCase(TestCase, LoginHelper, LessonHelper):
    """
    Contains the test cases for the delete lesson request view
    """

    def setUp(self):
        """
        Generate lesson request that will be deleted.
        """
        self._create_student_user()
        self._assign_lesson_request_to_user(self.student_user)

        self.lesson_request = self.student_user.student_profile.lesson_requests.first()
        self.url = reverse('delete_lesson_request', kwargs={ 'id': self.lesson_request.id })

    """
    Test cases
    """

    def test_url(self):
        self.assertEqual(self.url, f'/lesson-requests/delete/{ self.lesson_request.id }/')

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
        self.assertTemplateUsed(response, 'templates/lesson/delete_lesson_request.html')

    def test_delete_of_non_existent_lesson_request(self):
        self._log_in_as_student()

        before_count = LessonRequest.objects.count()
        url = reverse('delete_lesson_request', kwargs={ 'id': 2 })
        response = self.client.post(url, follow=True)
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

    def test_successful_delete_of_valid_lesson_request(self):
        self._log_in_as_student()

        before_count = LessonRequest.objects.count()
        url = reverse('delete_lesson_request', kwargs={ 'id': self.lesson_request.id })
        response = self.client.post(url, follow=True)
        after_count = LessonRequest.objects.count()

        # Check deletes have taken place
        self.assertEqual(before_count, after_count + 1)

        # Should redirect
        response_url = reverse('view_lesson_requests')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        # Should be success message on it
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.SUCCESS)

        self.assertFalse(LessonRequest.objects.filter(pk=self.lesson_request.id).exists())
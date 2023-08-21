from django.test import TestCase
from lessons.models.user_models import User, UserType, TeacherProfile
from lessons.forms.user_forms import *
from django.urls import reverse
from ..helpers import LoginHelper
from django.contrib import messages

class DeleteTeacherViewTestCase(TestCase, LoginHelper):
    """
    Contains the test cases for the delete teacher account view
    """

    def setUp(self):
        """
        Generate teacher user that will be deleted.
        """
        self._create_teacher_user()
        self._create_director_user()
        self.url = reverse('delete_teacher', kwargs={ 'email': self.teacher_user.username })

    """
    Test cases
    """

    def test_delete_teacher_url(self):
        """
        Test delete teacher url is correct
        """
        self.assertEqual(self.url, '/teachers/delete/teacher@example.com/')
    
    def test_view_restricted_for_guest(self):
        """
        Guest should not be able to access teacher view
        """
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_login(response=response)

    def test_view_restricted_for_student(self):
        """
        Student should not be able to access teacher view
        """
        self._create_student_user()
        self._log_in_as_student()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.STUDENT)

    def test_view_restricted_for_admin(self):
        """
        Admin should not be able to access teacher view
        """
        self._create_admin_user()
        self._log_in_as_admin()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.ADMIN)

    def test_view_restricted_for_teacher(self):
        """
        teacher should not be able to access teacher view
        """
        self._log_in_as_teacher()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.TEACHER)

    def test_view_allowed_for_director(self):
        """
        Director should be able to access teacher view
        """
        self._log_in_as_director()

        # Director should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/teacher/delete_teacher.html')

    def test_deletion_of_non_existent_user(self):
        """
        Attempt to delete non existent user will causer error message
        """
        self._log_in_as_director()

        before_user_count = User.objects.count()
        before_teacher_profile_count = TeacherProfile.objects.count()
        url = reverse('delete_teacher', kwargs={ 'email': 'invalid@example.com'})
        response = self.client.post(url, follow=True)
        after_user_count = User.objects.count()
        after_teacher_profile_count = TeacherProfile.objects.count()

        # Check no deletes have taken place
        self.assertEqual(before_teacher_profile_count, after_teacher_profile_count)
        self.assertEqual(before_user_count, after_user_count)

        # Should redirect to view teacher accounts page
        response_url = reverse('view_teachers')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'templates/teacher/view_teachers.html')

        # Should be error message on it
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.ERROR)

    def test_deletion_of_valid_user(self):
        """
        Attempt to delete valid user will be successful
        """
        self._log_in_as_director()

        before_user_count = User.objects.count()
        before_teacher_profile_count = TeacherProfile.objects.count()
        url = reverse('delete_teacher', kwargs={ 'email': 'teacher@example.com'})
        response = self.client.post(url, follow=True)
        after_user_count = User.objects.count()
        after_teacher_profile_count = TeacherProfile.objects.count()

        # Check deletes have taken place
        self.assertEqual(before_teacher_profile_count, after_teacher_profile_count + 1)
        self.assertEqual(before_user_count, after_user_count + 1)

        # Should redirect to view teacher accounts page
        response_url = reverse('view_teachers')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'templates/teacher/view_teachers.html')

        # Should be success message on it
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.SUCCESS)
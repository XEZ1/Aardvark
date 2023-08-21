from django.test import TestCase
from lessons.models.user_models import User, AdminProfile, UserType, TeacherProfile
from lessons.forms.user_forms import *
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from lessons.tests.helpers import LoginHelper

class RegisterTeacherViewTestCase(TestCase, LoginHelper):
    """
    Contains the test cases for the teacher registration view
    """

    def setUp(self):
        """
        Simulate the form input and get routed URL
        """
        # It is done this way so that if URL it altered in future, test doesn't break
        self.url = reverse('register_teacher')
        self._create_director_user()

        self.form_input = {
            'first_name': 'Jane',
            'last_name' : 'Doe',
            'email' : 'janedoe@example.com',
            'password' : 'Password123',
            'password_confirm' : 'Password123', }
        

    """
    Test cases
    """

    def test_register_url(self):
        self.assertEqual(self.url, '/register-teacher/')

    def test_teacher_view_restricted_for_guest(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_login(response)

    def test_get_register_for_director(self):
        self._log_in_as_director()

        # Director should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/teacher/register_teacher.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RegisterTeacherForm))

        # Shouldn't be bound as new instance
        self.assertFalse(form.is_bound)

    def test_view_restricted_for_admin(self):
        # Admin should be created and logged in
        self._create_admin_user()
        self._log_in_as_admin()

        # Admin should be logged in
        self.assertTrue(self._is_logged_in())

        # Check template used
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.ADMIN)

    def test_view_restricted_for_student(self):
        # Student should be created and logged in
        self._create_student_user()
        self._log_in_as_student()

        # Student should be logged in
        self.assertTrue(self._is_logged_in())

        # Check template used
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.STUDENT)

    def test_view_restricted_for_teacher(self):
        # Teacher should be created and logged in
        self._create_teacher_user()
        self._log_in_as_teacher()

        # Techer should be logged in
        self.assertTrue(self._is_logged_in())

        # Check template used
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.TEACHER)

        
    """
    RegisterTeacherForm
    """

    def test_unsuccesful_teacher_registration(self):
        # Director user logged in
        # Director required to create teacher
        self._log_in_as_director()

        # Director should be logged in
        self.assertTrue(self._is_logged_in())

        # Make form bad input
        self.form_input['email'] = 'bademail'

        # Check that insertions didn't occur
        before_user_count = User.objects.count()
        before_profile_count = TeacherProfile.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_user_count = User.objects.count()
        after_profile_count = TeacherProfile.objects.count()

        # Check both types of inserts have taken place
        self.assertEqual(before_profile_count, after_profile_count)
        self.assertEqual(before_user_count, after_user_count)

        # Check page still valid
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'templates/teacher/register_teacher.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RegisterTeacherForm))
        self.assertTrue(form.is_bound)

    def test_successful_teacher_registration(self):
        # Director user logged in
        # Director required to create teacher
        self._log_in_as_director()

        # Director should be logged in
        self.assertTrue(self._is_logged_in())

        before_user_count = User.objects.count()
        before_profile_count = TeacherProfile.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_user_count = User.objects.count()
        after_profile_count = TeacherProfile.objects.count()

        # Check both inserts have taken place
        self.assertEqual(before_profile_count, after_profile_count - 1)
        self.assertEqual(before_user_count, after_user_count - 1)

        # Check that response goes to next page
        response_url = reverse('register_teacher')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        user = User.objects.get(username = 'janedoe@example.com')

        # Check that response goes to correct dashboard
        self.assertTemplateUsed(response, 'templates/teacher/register_teacher.html')

        # Check that the fields went through to database
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.com')
        self.assertEqual(user.type, UserType.TEACHER)
        self.assertEqual(user.is_active, True)
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
        self.assertTrue(self._is_logged_in())
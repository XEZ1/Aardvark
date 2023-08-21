from django.test import TestCase
from lessons.models.user_models import User, StudentProfile, UserType, AdminProfile
from lessons.forms.user_forms import *
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from ..helpers import LoginHelper

class RegisterViewTestCase(TestCase, LoginHelper):
    """
    Contains the test cases for the student registration view
    """

    def setUp(self):
        """
        Simulate the form input and get routed URL
        """
        # It is done this way so that if URL it altered in future, test doesn't break
        self.url = reverse('register')

        

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
        self.assertEqual(self.url, '/register/')

    def test_get_register_for_guest(self):
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/student/register_student.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RegisterStudentForm))

        # Shouldn't be bound as new instance
        self.assertFalse(form.is_bound)

    def test_get_register_for_director(self):
        self._create_director_user()
        self._log_in_as_director()

        # Director should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/admin/register_admin.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RegisterAdminForm))

        # Shouldn't be bound as new instance
        self.assertFalse(form.is_bound)

    def test_get_register_for_parent(self):
        self._create_student_user()
        self._log_in_as_student()

    def test_view_restricted_for_admin(self):
        self._create_admin_user()
        self._log_in_as_admin()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.ADMIN)

    """
    RegisterStudentForm
    """

    def test_unsuccesful_student_registration(self):
        # Make form bad input
        self.form_input['email'] = 'bademail'

        # Check that insertions didn't occur
        before_user_count = User.objects.count()
        before_profile_count = StudentProfile.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_user_count = User.objects.count()
        after_profile_count = StudentProfile.objects.count()

        # Check no inserts have taken place
        self.assertEqual(before_profile_count, after_profile_count)
        self.assertEqual(before_user_count, after_user_count)

        # Check page still valid
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'templates/student/register_student.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RegisterStudentForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_successful_student_registration(self):
        before_user_count = User.objects.count()
        before_profile_count = StudentProfile.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_user_count = User.objects.count()
        after_profile_count = StudentProfile.objects.count()

        # Check both inserts have taken place
        self.assertEqual(before_profile_count, after_profile_count - 1)
        self.assertEqual(before_user_count, after_user_count - 1)

        # Check that response goes to next page
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        user = User.objects.get(username = 'janedoe@example.com')

        # Check that response goes to correct dashboard
        self.assertTemplateUsed(response, 'templates/student/student_dashboard.html')

        # Check that the fields went through to database
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.com')
        self.assertEqual(user.type, UserType.STUDENT)
        self.assertEqual(user.is_active, True)
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
        self.assertTrue(self._is_logged_in())

    def test_parent_for_registeration_child(self):
        self._create_student_user()
        self._create_secondary_student_user()
        self.student_user_2.student_profile.parent = self.student_user.student_profile
        self.student_user_2.student_profile.save()

        self._log_in_as_student()

        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/student/register_student_child.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RegisterStudentForm))

        # Shouldn't be bound as new instance
        self.assertFalse(form.is_bound)

    def test_view_restricted_for_student_child(self):
        """
        Student children shouldn't able to register children themselves
        """
        self._create_student_user()

        # Assign student_user_2 to be the child of student_user        
        self._create_secondary_student_user()
        self.student_user_2.student_profile.parent = self.student_user.student_profile
        self.student_user_2.student_profile.save()

        # Log in
        self._log_in_as_student_2()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.STUDENT)

    def test_get_register_for_student_parent(self):
        self._create_student_user()    
        self._create_secondary_student_user()
        self.student_user_2.student_profile.parent = self.student_user.student_profile
        self.student_user_2.student_profile.save()

        # Log in
        self._log_in_as_student()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/student/register_student_child.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RegisterStudentForm))

        # Shouldn't be bound as new instance
        self.assertFalse(form.is_bound)

    """
    RegisterAdminForm
    """

    def test_unsuccesful_admin_registration(self):
        self._create_director_user()
        self._log_in_as_director()

        # Director should be logged in
        self.assertTrue(self._is_logged_in())

        # Make form bad input
        self.form_input['email'] = 'bademail'

        # Check that insertions didn't occur
        before_user_count = User.objects.count()
        before_profile_count = AdminProfile.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_user_count = User.objects.count()
        after_profile_count = AdminProfile.objects.count()

        # Check both types of inserts have taken place
        self.assertEqual(before_profile_count, after_profile_count)
        self.assertEqual(before_user_count, after_user_count)

        # Check page still valid
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'templates/admin/register_admin.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RegisterAdminForm))
        self.assertTrue(form.is_bound)

    def test_succesful_admin_registration(self):
        self._create_director_user()
        self._log_in_as_director()

        # Director should be logged in
        self.assertTrue(self._is_logged_in())

        # Check that insertions happened correctly
        before_user_count = User.objects.count()
        before_profile_count = AdminProfile.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_user_count = User.objects.count()
        after_profile_count = AdminProfile.objects.count()

        # Check both types of inserts have taken place
        self.assertEqual(before_profile_count, after_profile_count - 1)
        self.assertEqual(before_user_count, after_user_count - 1)

        # Check that response redirects to same page
        response_url = reverse('register')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        # Should be one message for success
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)

        # Check that the fields went through to database
        user = User.objects.get(username = 'janedoe@example.com')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.com')
        self.assertEqual(user.type, UserType.ADMIN)
        self.assertEqual(user.is_active, True)
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)

    
            
    def test_succesful_parent_registration(self):
        self._create_student_user()    
        self._create_secondary_student_user()
        self.student_user_2.student_profile.parent = self.student_user.student_profile
        self.student_user_2.student_profile.save()
        self._log_in_as_student()

        # Director should be logged in
        self.assertTrue(self._is_logged_in())

        # Check that insertions happened correctly
        response = self.client.post(self.url, self.form_input, follow=True)
        

        # Check that response redirects to same page
        response_url = reverse('register')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        # Should be one message for success
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)

        # Check that the fields went through to database
        user = User.objects.get(username = 'janedoe@example.com')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.com')
        self.assertEqual(user.type, UserType.STUDENT)
        self.assertEqual(user.is_active, True)
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
        self.assertTrue(user.student_profile.parent, self.student_user)
        
    def test_unsuccesful_parent_registration(self):
        self._create_student_user()    
        self._create_secondary_student_user()
        self.student_user_2.student_profile.parent = self.student_user.student_profile
        self.student_user_2.student_profile.save()

        #log in as parent
        self._log_in_as_student()
        self.assertTrue(self._is_logged_in())

        # Make form bad input
        self.form_input['email'] = 'bademail'

        # Check that insertions didn't occur
        before_user_count = User.objects.count()
        before_profile_count = StudentProfile.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_user_count = User.objects.count()
        after_profile_count = StudentProfile.objects.count()

        # Check both types of inserts have taken place
        self.assertEqual(before_profile_count, after_profile_count)
        self.assertEqual(before_user_count, after_user_count)

        #check if the insertions are incorrect
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(isinstance(form, RegisterStudentForm))
        self.assertTrue(form.is_bound)





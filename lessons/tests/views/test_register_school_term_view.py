from django.test import TestCase
from lessons.models.user_models import UserType
from lessons.forms.user_forms import *
from lessons.forms.term_forms import *
from django.urls import reverse
from ..helpers import LoginHelper

class RegisterSchoolTermViewTestCase(TestCase, LoginHelper):
    """
    Contains the test cases for the school term registration view
    """

    def setUp(self):
        """
        Simulate the form input and get routed URL
        """

        self.url = reverse('register_school_term')

        self.form_input = {
            'label': 'Term 1',
            'start_date' : '2022-01-01',#yyyy-mm-dd
            'end_date' : '2022-01-30',
        }

    """
    Test cases
    """

    def test_register_url(self):
        self.assertEqual(self.url, '/register-school-term/')

    def test_get_register_for_director(self):
        self._create_director_user()
        self._log_in_as_director()

        # Director should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/term/register_school_term.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RegisterSchoolTermForm))

        # Shouldn't be bound as new instance
        self.assertFalse(form.is_bound)

    def test_get_register_for_admin(self):
        self._create_admin_user()
        self._log_in_as_admin()

        # Director should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/term/register_school_term.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RegisterSchoolTermForm))

        # Shouldn't be bound as new instance
        self.assertFalse(form.is_bound)

    def test_view_restricted_for_student(self):
        self._create_student_user()
        self._log_in_as_student()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.STUDENT)

    def test_view_restricted_for_guest(self):
        response = self.client.get(self.url, follow=True)

        # Check template used
        self.assertTemplateUsed(response, 'templates/log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LoginUserForm))

        # Shouldn't be bound as new instance
        self.assertFalse(form.is_bound)
        
    def test_unsuccesful_term_registration(self):
        self._create_admin_user()
        self._log_in_as_admin()
        self.assertTrue(self._is_logged_in())

        self.form_input['label'] = ''

        before_count = SchoolTerm.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = SchoolTerm.objects.count()

        # Check no inserts have taken place
        self.assertEqual(before_count, after_count)

        # Check page still valid
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'templates/term/register_school_term.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RegisterSchoolTermForm))
        self.assertTrue(form.is_bound)

    def test_successful_term_registration(self):
        self._create_admin_user()
        self._log_in_as_admin()
        self.assertTrue(self._is_logged_in())

        before_count = SchoolTerm.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = SchoolTerm.objects.count()
        self.assertEqual(before_count, after_count - 1)

        # Check that response is correct
        self.assertRedirects(response, reverse("register_school_term"), status_code=302, target_status_code=200)

        # Check that the fields went through to database
        term = SchoolTerm.objects.get(label = 'Term 1')
        self.assertEqual(term.label, 'Term 1')
        self.assertEqual(term.start_date.strftime("%Y-%m-%d"), '2022-01-01')
        self.assertEqual(term.end_date.strftime("%Y-%m-%d"), '2022-01-30')
from django.test import TestCase
from lessons.models.user_models import UserType
from lessons.forms.user_forms import *
from django.urls import reverse
from ..helpers import LoginHelper, LessonHelper
from lessons.models.term_models import *

class ViewSchoolTermsViewTestCase(TestCase, LoginHelper, LessonHelper):
    """
    Contains the test cases for the view school terms view
    """

    def setUp(self):
        """
        Get routed URL
        """

        self.url = reverse('view_school_terms')

        school_term = SchoolTerm()
        school_term.label= "Term 1"
        school_term.start_date= '2022-01-01'
        school_term.end_date= '2022-01-30'
        school_term.save()

        school_term_2 = SchoolTerm()
        school_term_2.label= "Term 2"
        school_term_2.start_date= '2022-02-01'
        school_term_2.end_date= '2022-02-28'
        school_term_2.save()

    """
    Test cases
    """

    def test_url(self):
        self.assertEqual(self.url, '/school-terms/')
    
    def test_view_restricted_for_guest(self):
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_login(response)
        

    def test_view_restricted_for_student(self):
        self._create_student_user()
        self._log_in_as_student()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response, UserType.STUDENT)

    def test_get_school_terms_for_admin(self):
        self._create_admin_user()
        self._log_in_as_admin()

        #admin should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/term/view_school_terms.html')

        #all school terms should be displayed
        terms = response.context['terms']
        self.assertEqual(len(terms), 2)


    def test_get_school_terms_for_director(self):
        self._create_director_user()
        self._log_in_as_director()

        # Director should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/term/view_school_terms.html')

        #all school terms should be displayed
        terms = response.context['terms']
        self.assertEqual(len(terms), 2)
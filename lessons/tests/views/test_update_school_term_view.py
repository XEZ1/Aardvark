from django.test import TestCase
from lessons.models.user_models import UserType
from lessons.models.term_models import SchoolTerm
from lessons.forms.term_forms import *
from lessons.forms.user_forms import *
from django.urls import reverse
from ..helpers import LoginHelper, LessonHelper
from django.contrib import messages
from lessons.models.lesson_models import *

class UpdateLessonRequestViewTestCase(TestCase, LoginHelper, LessonHelper):
    """
    Contains the test cases for the update lesson request view
    """

    def setUp(self):
        """
        Simulate the form input on view
        """
        
        self._create_admin_user()

        self.school_term = SchoolTerm()
        self.school_term.label= "Term 1"
        self.school_term.start_date= '2022-01-01'
        self.school_term.end_date= '2022-01-30'
        self.school_term.save()

        school_term_2 = SchoolTerm()
        school_term_2.label= "Term 2"
        school_term_2.start_date= '2022-02-01'
        school_term_2.end_date= '2022-02-28'
        school_term_2.save()

        self.form_input = {
            'label': 'Term 3',
            'start_date' : '2022-03-01',#yyyy-mm-dd
            'end_date' : '2022-03-31',
        }

        self.url = reverse('update_school_term', kwargs={ 'id': self.school_term.id })

    """
    Test cases
    """

    def test_update_url(self):
        self.assertEqual(self.url, f'/school-terms/update/{ self.school_term.id }/')
    
    def test_get_update_for_director(self):
        self._create_director_user()
        self._log_in_as_director()

        # Director should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/term/update_school_term.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UpdateSchoolTermForm))

        # Shouldn't be bound as new instance
        self.assertFalse(form.is_bound)

    def test_get_register_for_admin(self):
        self._log_in_as_admin()

        #admin should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/term/update_school_term.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UpdateSchoolTermForm))

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


    def test_update_of_non_existent_term(self):
        self._log_in_as_admin()

        url = reverse('update_school_term', kwargs={ 'id': 100 })
        response = self.client.post(url, self.form_input, follow=True)

        # Should redirect to view page
        response_url = reverse('view_school_terms')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        # Should be error message on it
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.ERROR)


    def test_successful_update_of_valid_term(self):
        self._log_in_as_admin()

        url = reverse('update_school_term', kwargs={ 'id': self.school_term.id })
        response = self.client.post(url, self.form_input, follow=True)

        # Should redirect
        response_url = reverse('view_school_terms')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        # Should be success message on it
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.SUCCESS)

        school_term = SchoolTerm.objects.get(pk=self.school_term.id)

        self.assertEqual(school_term.label, 'Term 3')
        self.assertEqual(school_term.start_date.strftime("%Y-%m-%d"), '2022-03-01')
        self.assertEqual(school_term.end_date.strftime("%Y-%m-%d"), '2022-03-31')

    def test_unsuccessful_update_of_valid_term(self):
        self.form_input['label'] = '' # Should cause error
        self._log_in_as_admin()

        url = reverse('update_school_term', kwargs={ 'id': self.school_term.id })
        response = self.client.post(url, self.form_input, follow=True)

        # Should rerender same page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'templates/term/update_school_term.html')

        # Model should be unchanged
        term = SchoolTerm.objects.get(label = 'Term 1')
        self.assertEqual(term.label, 'Term 1')
        self.assertEqual(term.start_date.strftime("%Y-%m-%d"), '2022-01-01')
        self.assertEqual(term.end_date.strftime("%Y-%m-%d"), '2022-01-30')
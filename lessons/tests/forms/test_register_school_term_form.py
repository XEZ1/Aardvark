from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models.user_models import User, AdminProfile, UserType
from lessons.forms.term_forms import *
from django import forms
from django.contrib.auth.hashers import check_password

class RegisterSchoolTermFormTestCase(TestCase):
    """
    Contains the test cases for the register term form
    """

    def setUp(self):
        """
        Simulate the form input
        """
        self.form_input = {
            'label': 'Term 1',
            'start_date' : '2022-01-01', #yyyy-mm-dd
            'end_date' : '2022-01-30',
        }

    def test_valid_form(self):
        form = RegisterSchoolTermForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = RegisterSchoolTermForm()

        # Check that label field is present
        self.assertIn('label', form.fields)
        
        #check that other fields are within form
        self.assertIn('start_date', form.fields)
        start_date_field = form.fields['start_date']
        self.assertTrue(isinstance(start_date_field, forms.DateField))

        self.assertIn('end_date', form.fields)
        end_date_field = form.fields['end_date']
        self.assertTrue(isinstance(end_date_field, forms.DateField))

    def test_form_uses_model_validation(self):
        self.form_input['label'] = ''
        form = RegisterSchoolTermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_start_date_must_be_before_end_date(self):
        self.form_input['start_date'] = '2022-02-01'
        form = RegisterSchoolTermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_start_date_must_not_be_equal_to_end_date(self):
        self.form_input['start_date'] = '2022-01-30'
        form = RegisterSchoolTermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_term_must_not_overlap_existing_1(self):
        school_term = SchoolTerm()
        school_term.label= "Term 2"
        school_term.start_date= '2022-01-30'
        school_term.end_date= '2022-02-28'
        school_term.save()

        form = RegisterSchoolTermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_term_must_not_overlap_existing_2(self):
        school_term = SchoolTerm()
        school_term.label= "Term 2"
        school_term.start_date= '2022-01-29'
        school_term.end_date= '2022-02-28'
        school_term.save()

        form = RegisterSchoolTermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = RegisterSchoolTermForm(data=self.form_input)

        before_term_count = SchoolTerm.objects.count()
        form.save()
        after_term_count = SchoolTerm.objects.count()

        self.assertEqual(before_term_count, after_term_count - 1)

        term = SchoolTerm.objects.get(label = 'Term 1')
        
        self.assertEqual(term.label, 'Term 1')
        self.assertEqual(term.start_date.strftime("%Y-%m-%d"), '2022-01-01')
        self.assertEqual(term.end_date.strftime("%Y-%m-%d"), '2022-01-30')
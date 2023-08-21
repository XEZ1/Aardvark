from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models.user_models import User, AdminProfile, UserType
from lessons.models.lesson_models import *
from lessons.forms.user_forms import *
from lessons.forms.lesson_forms import *
from django import forms
from django.contrib.auth.hashers import check_password
from lessons.tests.helpers import LoginHelper, LessonHelper

class UpdateLessonRequestFormTestCase(TestCase, LoginHelper, LessonHelper):
    """
    Contains the test cases for the update lesson request form
    """

    def setUp(self):
        """
        Simulate the form input
        """

        self._create_student_user()
        self._assign_lesson_request_to_user(self.student_user)

        self.lesson_request = self.student_user.student_profile.lesson_requests.first()
        self.form_input = {
            'interval': '2',
            'duration': '45',
            'quantity': '3',
            'notes': 'Please can I have example teacher 2',
            'availability': [AvailabilityPeriod.TUESDAY] }

    """
    Test cases
    """

    def test_valid_form(self):
        form = UpdateLessonRequestForm(data=self.form_input, instance=self.lesson_request)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = UpdateLessonRequestForm()

        # Check that fields are present
        self.assertIn('interval', form.fields)
        self.assertIn('duration', form.fields)
        self.assertIn('quantity', form.fields)
        self.assertIn('notes', form.fields)

        self.assertIn('availability', form.fields)
        self.assertTrue(isinstance(form.fields['availability'], forms.MultipleChoiceField))
        self.assertTrue(isinstance(form.fields['availability'].widget, forms.CheckboxSelectMultiple))

    def test_form_must_have_selected_availabilty(self):
        self.form_input['availability'] = '' # Empty availability selection
        form = UpdateLessonRequestForm(data=self.form_input, instance=self.lesson_request)
        self.assertFalse(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['interval'] = '5'
        form = UpdateLessonRequestForm(data=self.form_input, instance=self.lesson_request)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = UpdateLessonRequestForm(data=self.form_input, instance=self.lesson_request)

        before_count = LessonRequest.objects.count()
        form.save()
        after_count = LessonRequest.objects.count()

        # No records should've been inserted
        self.assertEqual(before_count, after_count)

        lesson_request = LessonRequest.objects.get(pk=self.lesson_request.id)

        self.assertEqual(lesson_request.duration, 45)
        self.assertEqual(lesson_request.interval, 2)
        self.assertEqual(lesson_request.quantity, 3)
        self.assertEqual(lesson_request.notes, 'Please can I have example teacher 2')
        self.assertEqual(lesson_request.availability, 'TUESDAY') # Cleans data correctly
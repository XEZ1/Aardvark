from django.test import TestCase
from lessons.models.user_models import User, StudentProfile, UserType
from lessons.models.lesson_models import LessonRequest
from lessons.forms.user_forms import *
from lessons.forms.lesson_forms import *
from django import forms
from django.contrib.auth.hashers import check_password
from lessons.tests.helpers import LoginHelper

class RequestLessonFormTestCase(TestCase, LoginHelper):
    """
    Contains the test cases for the request lesson form
    """

    def setUp(self):
        """
        Simulate the form input
        """
        self._create_student_user()
        self.form_input = {
            'interval': '1',
            'duration': '60',
            'quantity': '2',
            'notes': 'Please can I have example teacher',
            'availability': [AvailabilityPeriod.MONDAY, AvailabilityPeriod.TUESDAY],
            'recipient_profile_id': self.student_user.student_profile.id
            }

    """
    Test cases
    """

    def test_valid_request_lesson_form(self):
        form = RequestLessonForm(self.student_user, data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = RequestLessonForm(self.student_user)

        # Check that fields are present
        self.assertIn('interval', form.fields)
        self.assertIn('duration', form.fields)
        self.assertIn('quantity', form.fields)
        self.assertIn('notes', form.fields)
        self.assertIn('recipient_profile_id', form.fields)

        self.assertIn('availability', form.fields)
        self.assertTrue(isinstance(form.fields['availability'], forms.MultipleChoiceField))
        self.assertTrue(isinstance(form.fields['availability'].widget, forms.CheckboxSelectMultiple))

    def test_form_shows_user_children(self):
        # Assign student_user_2 to be the child of student_user        
        self._create_secondary_student_user()
        self.student_user_2.student_profile.parent = self.student_user.student_profile
        self.student_user_2.student_profile.save()

        form = RequestLessonForm(self.student_user)
        self.assertEqual(len(form.fields['recipient_profile_id'].choices), 2)

    def test_form_must_have_selected_availabilty(self):
        self.form_input['availability'] = '' # Empty availability selection
        form = RequestLessonForm(self.student_user, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['interval'] = '5'
        form = RequestLessonForm(self.student_user, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = RequestLessonForm(self.student_user, data=self.form_input)

        before_count = LessonRequest.objects.count()
        form.save()
        after_count = LessonRequest.objects.count()

        self.assertEqual(before_count, after_count - 1)

        lesson_request = self.student_user.student_profile.lesson_requests.first()

        self.assertEqual(lesson_request.duration, 60)
        self.assertEqual(lesson_request.interval, 1)
        self.assertEqual(lesson_request.quantity, 2)
        self.assertEqual(lesson_request.notes, 'Please can I have example teacher')
        self.assertEqual(lesson_request.availability, 'MONDAY,TUESDAY') # Cleans data correctly
        self.assertEqual(lesson_request.student_profile, self.student_user.student_profile)
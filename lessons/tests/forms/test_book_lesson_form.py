from django.test import TestCase
from lessons.models.user_models import User, StudentProfile, UserType
from lessons.models.lesson_models import LessonRequest
from lessons.forms.user_forms import *
from lessons.forms.lesson_forms import *
from django import forms
from django.contrib.auth.hashers import check_password
from lessons.tests.helpers import LoginHelper, LessonHelper, SchoolTermHelper
from datetime import datetime, timedelta

class RequestLessonFormTestCase(TestCase, LoginHelper, LessonHelper, SchoolTermHelper):
    """
    Contains the test cases for the book lesson form
    """

    def setUp(self):
        """
        Simulate the form input
        """
        self._create_teacher_user()
        self._create_student_user()
        self._assign_lesson_request_to_user(self.student_user)
        self._create_admin_user()
        self._create_school_term()

        self.lesson_request = self.student_user.student_profile.lesson_requests.first()
        self.time = datetime.now().time()
        self.date = datetime.now()
        self.form_input = {
            'school_term': self.school_term,
            'start_date': self.date.strftime("%Y-%m-%d"),
            'end_date': (self.date + timedelta(days=30)).strftime("%Y-%m-%d"),
            'teacher': self.teacher_user.teacher_profile,
            'regular_day': AvailabilityPeriod.MONDAY,
            'regular_start_time': self.time,
            'interval': '1',
            'duration': '60',
            'quantity': '2', 
            }

    """
    Test cases
    """

    def test_valid_form(self):
        form = BookLessonForm(self.admin_user, self.lesson_request, data=self.form_input)
        self.assertTrue(form.is_valid())
        
    def test_form_has_necessary_fields(self):
        form = BookLessonForm(self.admin_user, self.lesson_request)

        # Check that fields are present
        self.assertIn('school_term', form.fields)
        self.assertIn('start_date', form.fields)
        self.assertIn('end_date', form.fields)
        self.assertIn('interval', form.fields)
        self.assertIn('duration', form.fields)
        self.assertIn('quantity', form.fields)
        self.assertIn('teacher', form.fields)
        self.assertIn('regular_day', form.fields)
        self.assertIn('regular_start_time', form.fields)

        self.assertTrue(isinstance(form.fields['regular_start_time'], forms.TimeField))
        self.assertTrue(isinstance(form.fields['start_date'], forms.DateField))

    def test_form_uses_model_validation(self):
        self.form_input['interval'] = '5'
        form = BookLessonForm(self.admin_user, self.lesson_request, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_start_date_cannot_be_outside_term_time(self):
        self.form_input['start_date'] = (self.date - timedelta(days=20)).strftime("%Y-%m-%d")
        form = BookLessonForm(self.admin_user, self.lesson_request, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_end_date_cannot_be_outside_term_time(self):
        self.form_input['end_date'] = (self.date + timedelta(days=200)).strftime("%Y-%m-%d")
        form = BookLessonForm(self.admin_user, self.lesson_request, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_quantity_cannot_be_higher_than_possible(self):
        # Ensures that other validation doesn't cause issue
        self.lesson_request.quantity = 20
        self.lesson_request.save()

        """
        The created term is 90 days in length
        With an interval of 1 week, a maximum of 13 lessons are possible
        """
        self.assertEqual(self.school_term.max_amount_of_lessons(1, self.school_term.start_date, self.school_term.end_date), 13)

        # Use term dates
        self.form_input['start_date'] = ''
        self.form_input['end_date'] = ''

        # Set quantity higher than possible
        self.form_input['quantity'] = 14

        form = BookLessonForm(self.admin_user, self.lesson_request, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_duration_can_not_be_longer_than_requested(self):
        self.lesson_request.duration = 45
        self.form_input['duration'] = '60'
        form = BookLessonForm(self.admin_user, self.lesson_request, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_quantity_can_not_be_longer_than_requested(self):
        self.lesson_request.quantity = 2
        self.form_input['quantity'] = '3'
        form = BookLessonForm(self.admin_user, self.lesson_request, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_start_date_can_not_be_in_past(self):
        self.form_input['start_date'] = (self.date - timedelta(days=2)).strftime("%Y-%m-%d")
        form = BookLessonForm(self.admin_user, self.lesson_request, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_regular_day_can_not_be_when_student_is_unavailable(self):
        self.form_input['regular_day'] = AvailabilityPeriod.FRIDAY # Student not available
        form = BookLessonForm(self.admin_user, self.lesson_request, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = BookLessonForm(self.admin_user, self.lesson_request, data=self.form_input)

        before_count = LessonBooking.objects.count()
        form.save()
        after_count = LessonBooking.objects.count()

        self.assertEqual(before_count, after_count - 1)

        lesson_booking = LessonBooking.objects.first()

        self.assertEqual(lesson_booking.school_term, self.school_term)
        self.assertEqual(lesson_booking.start_date.strftime("%Y-%m-%d"), self.date.strftime("%Y-%m-%d")) 
        self.assertEqual(lesson_booking.end_date.strftime("%Y-%m-%d"), (self.date + timedelta(days=30)).strftime("%Y-%m-%d")) 
        self.assertEqual(lesson_booking.duration, 60)
        self.assertEqual(lesson_booking.interval, 1)
        self.assertEqual(lesson_booking.quantity, 2)
        self.assertEqual(lesson_booking.teacher, self.teacher_user.teacher_profile)
        self.assertEqual(lesson_booking.regular_day, AvailabilityPeriod.MONDAY) 
        self.assertEqual(lesson_booking.regular_start_time, self.time) 
        self.assertEqual(lesson_booking.lesson_request, self.lesson_request) 
        self.assertEqual(lesson_booking.admin_profile, self.admin_user.admin_profile) 

    def test_form_must_save_correctly_with_blank_start_and_end_dates(self):
        self.form_input['start_date'] = ''
        self.form_input['end_date'] = ''

        form = BookLessonForm(self.admin_user, self.lesson_request, data=self.form_input)

        before_count = LessonBooking.objects.count()
        form.save()
        after_count = LessonBooking.objects.count()

        self.assertEqual(before_count, after_count - 1)

        lesson_booking = LessonBooking.objects.first()

        self.assertEqual(lesson_booking.school_term, self.school_term)
        self.assertEqual(lesson_booking.start_date, None) 
        self.assertEqual(lesson_booking.end_date, None) 
        self.assertEqual(lesson_booking.duration, 60)
        self.assertEqual(lesson_booking.interval, 1)
        self.assertEqual(lesson_booking.quantity, 2)
        self.assertEqual(lesson_booking.teacher, self.teacher_user.teacher_profile)
        self.assertEqual(lesson_booking.regular_day, AvailabilityPeriod.MONDAY) 
        self.assertEqual(lesson_booking.regular_start_time, self.time) 
        self.assertEqual(lesson_booking.lesson_request, self.lesson_request) 
        self.assertEqual(lesson_booking.admin_profile, self.admin_user.admin_profile) 
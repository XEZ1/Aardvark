from django.test import TestCase
from lessons.models.user_models import User, StudentProfile, UserType
from lessons.models.lesson_models import LessonRequest
from lessons.forms.user_forms import *
from lessons.forms.lesson_forms import *
from django import forms
from django.contrib.auth.hashers import check_password
from lessons.tests.helpers import LoginHelper, LessonHelper, SchoolTermHelper
from datetime import datetime, timedelta

class UpdateLessonBookingFormTestCase(TestCase, LoginHelper, LessonHelper, SchoolTermHelper):
    """
    Contains the test cases for the update lesson booking form
    """

    def setUp(self):
        """
        Simulate the form input
        """
        self._create_student_user()
        self._create_teacher_user()
        self._create_secondary_teacher_user()
        self._assign_lesson_request_to_user(self.student_user)
        self._create_admin_user()
        self._create_school_term()
        self._assign_lesson_booking_to_lesson_request(self.student_user.student_profile.lesson_requests.first())
        
        self.lesson_booking = self.admin_user.admin_profile.lesson_bookings.first()
        self.date = datetime.now() + timedelta(days=1)
        self.time = self.lesson_booking.regular_start_time
        self.form_input = {
            'school_term': self.school_term,
            'start_date': self.date.strftime("%Y-%m-%d"),
            'end_date': (self.date + timedelta(days=30)).strftime("%Y-%m-%d"),
            'teacher': self.teacher_user_2.teacher_profile.id,
            'regular_day': AvailabilityPeriod.TUESDAY,
            'regular_start_time': self.time,
            'interval': '2',
            'duration': '45',
            'quantity': '1', 
            }

    """
    Test cases
    """

    def test_valid_form(self):
        form = UpdateLessonBookingForm(data=self.form_input, instance=self.lesson_booking)
        form.is_valid()
        self.assertTrue(form.is_valid())
        
    def test_form_has_necessary_fields(self):
        form = UpdateLessonBookingForm(data=self.form_input, instance=self.lesson_booking)

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
        form = UpdateLessonBookingForm(data=self.form_input, instance=self.lesson_booking)
        self.assertFalse(form.is_valid())

    def test_start_date_cannot_be_outside_term_time(self):
        self.form_input['start_date'] = (self.date - timedelta(days=20)).strftime("%Y-%m-%d")
        form = UpdateLessonBookingForm(data=self.form_input, instance=self.lesson_booking)
        self.assertFalse(form.is_valid())

    def test_end_date_cannot_be_outside_term_time(self):
        self.form_input['end_date'] = (self.date + timedelta(days=200)).strftime("%Y-%m-%d")
        form = UpdateLessonBookingForm(data=self.form_input, instance=self.lesson_booking)
        self.assertFalse(form.is_valid())

    def test_quantity_cannot_be_higher_than_possible(self):
        # Ensures that other validation doesn't cause issue
        self.lesson_booking.lesson_request.quantity = 20
        self.lesson_booking.lesson_request.save()

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

        form = UpdateLessonBookingForm(data=self.form_input, instance=self.lesson_booking)
        self.assertFalse(form.is_valid())

    def test_duration_can_not_be_longer_than_requested(self):
        self.lesson_booking.lesson_request.duration = 45
        self.form_input['duration'] = 60
        form = UpdateLessonBookingForm(data=self.form_input, instance=self.lesson_booking)
        self.assertFalse(form.is_valid())

    def test_quantity_can_not_be_longer_than_requested(self):
        self.lesson_booking.lesson_request.quantity = 2
        self.form_input['quantity'] = '3'
        form = UpdateLessonBookingForm(data=self.form_input, instance=self.lesson_booking)
        self.assertFalse(form.is_valid())

    def test_start_date_can_not_be_in_past(self):
        self.form_input['start_date'] = (self.date - timedelta(days=2)).strftime("%Y-%m-%d")
        form = UpdateLessonBookingForm(data=self.form_input, instance=self.lesson_booking)
        self.assertFalse(form.is_valid())

    def test_regular_day_can_not_be_when_student_is_unavailable(self):
        self.form_input['regular_day'] = AvailabilityPeriod.FRIDAY # Student not available
        form = UpdateLessonBookingForm(data=self.form_input, instance=self.lesson_booking)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = UpdateLessonBookingForm(data=self.form_input, instance=self.lesson_booking)

        before_count = LessonBooking.objects.count()
        form.save()
        after_count = LessonBooking.objects.count()

        # No records should be inserted
        self.assertEqual(before_count, after_count)

        self.lesson_booking = LessonBooking.objects.get(pk=self.lesson_booking.id)

        self.assertEqual(self.lesson_booking.start_date.strftime("%Y-%m-%d"), self.date.strftime("%Y-%m-%d")) 
        self.assertEqual(self.lesson_booking.end_date.strftime("%Y-%m-%d"), (self.date + timedelta(days=30)).strftime("%Y-%m-%d")) 
        self.assertEqual(self.lesson_booking.school_term, self.school_term) 
        self.assertEqual(self.lesson_booking.duration, 45)
        self.assertEqual(self.lesson_booking.interval, 2)
        self.assertEqual(self.lesson_booking.quantity, 1)
        self.assertEqual(self.lesson_booking.teacher.id, self.teacher_user_2.teacher_profile.id)
        self.assertEqual(self.lesson_booking.regular_day, AvailabilityPeriod.TUESDAY) 
        self.assertEqual(self.lesson_booking.regular_start_time, self.time) 
        self.assertEqual(self.lesson_booking.admin_profile, self.admin_user.admin_profile) 
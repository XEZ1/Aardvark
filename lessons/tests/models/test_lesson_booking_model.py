from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models.user_models import User, UserType
from lessons.models.lesson_models import *
from lessons.models.lesson_models import LessonRequest, AvailabilityPeriod
from lessons.tests.helpers import LoginHelper, LessonHelper, SchoolTermHelper
from datetime import datetime, timedelta, time

class LessonBookingModelTestCase(TestCase, LoginHelper, LessonHelper, SchoolTermHelper):
    """
    Contains the test cases for the the lesson booking model
    """
    def setUp(self):
        """
        Create a student user with a lesson request that will be associated with the lesson booking
        """
        self._create_teacher_user()
        self._create_student_user()
        self._create_admin_user()
        self._assign_lesson_request_to_user(self.student_user)
        self._create_school_term()

        self.lesson_booking = LessonBooking()

        # Django datetime to string docs: https://docs.djangoproject.com/en/dev/ref/settings/#date-input-formats
        self.lesson_booking.school_term = self.school_term
        self.lesson_booking.start_date = datetime.now()
        self.lesson_booking.end_date = datetime.now() + timedelta(days=30)
        self.lesson_booking.interval = 1
        self.lesson_booking.quantity = 2
        self.lesson_booking.duration = 60
        self.lesson_booking.teacher = self.teacher_user.teacher_profile
        self.lesson_booking.regular_day = AvailabilityPeriod.MONDAY
        self.lesson_booking.regular_start_time = time(hour=10)

        self.lesson_booking.lesson_request = self.student_user.student_profile.lesson_requests.first()
        self.lesson_booking.admin_profile = self.admin_user.admin_profile

    """
    Helper functions
    """

    def _assert_model_is_valid(self):
        try:
            self.lesson_booking.full_clean()
        except (ValidationError):
            self.fail('Test setup model should be valid')

    def _assert_model_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.lesson_booking.full_clean()

    """
    Test cases
    """

    def test_valid_model(self):
        self._assert_model_is_valid()

    def test_end_time_correct(self):
        self.assertEqual(self.lesson_booking.end_time(), time(hour=11))

    def test_dates_with_only_term(self):
        self.lesson_booking.start_date = None
        self.lesson_booking.end_date = None
        self.lesson_booking.save()

        self.assertEqual(self.lesson_booking.start_date_actual(), self.lesson_booking.school_term.start_date)
        self.assertEqual(self.lesson_booking.end_date_actual(), self.lesson_booking.school_term.end_date)

    def test_dates_with_custom_specified(self):
        self.assertEqual(self.lesson_booking.start_date_actual(), self.lesson_booking.start_date)
        self.assertEqual(self.lesson_booking.end_date_actual(), self.lesson_booking.end_date)

    def test_interval_cannot_be_empty(self):
        self.lesson_booking.interval = None
        self._assert_model_is_invalid()

    def test_duration_cannot_be_empty(self):
        self.lesson_booking.duration = None
        self._assert_model_is_invalid()

    def test_quantity_cannot_be_empty(self):
        self.lesson_booking.quantity = None
        self._assert_model_is_invalid()

    def test_admin_profile_cannot_be_empty(self):
        self.lesson_booking.admin_profile = None
        self._assert_model_is_invalid()

    def test_lesson_request_cannot_be_empty(self):
        self.lesson_booking.lesson_request = None
        self._assert_model_is_invalid()

    def test_admin_profile_cannot_be_empty(self):
        self.lesson_booking.admin_profile = None
        self._assert_model_is_invalid()

    def test_start_date_can_be_empty(self):
        self.lesson_booking.start_date = ''
        self._assert_model_is_valid()

    def test_end_date_can_be_empty(self):
        self.lesson_booking.end_date = ''
        self._assert_model_is_valid()

    def test_short_interval_formatted_correctly(self):
        self.assertEqual(self.lesson_booking.interval_formatted(), "1 week")

    def test_long_interval_formatted_correctly(self):
        self.lesson_booking.interval = 2
        self.assertEqual(self.lesson_booking.interval_formatted(), "2 weeks")

    def test_duration_formatted_correctly(self):
        self.assertEqual(self.lesson_booking.duration_formatted(), "60 minutes")

    def test_quantity_cannot_be_0(self):
        self.lesson_booking.quantity = 0
        self._assert_model_is_invalid()

    def test_quantity_cannot_be_26(self):
        self.lesson_booking.quantity = 0
        self._assert_model_is_invalid()

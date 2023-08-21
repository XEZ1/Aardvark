from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models.user_models import User, UserType
from lessons.models.lesson_models import LessonRequest, AvailabilityPeriod
from lessons.tests.helpers import LoginHelper

class LessonRequestModelTestCase(TestCase, LoginHelper):
    """
    Contains the test cases for the the lesson request model
    """
    def setUp(self):
        """
        Create a student user that will be associated with the lesson request
        """
        self._create_student_user()

        self.lesson_request = LessonRequest()

        self.lesson_request.interval = 1
        self.lesson_request.quantity = 2
        self.lesson_request.duration = 60
        self.lesson_request.notes = "Test notes"
        self.lesson_request.availability = 'MONDAY, TUESDAY'
        self.lesson_request.student_profile = self.student_user.student_profile

    """
    Helper functions
    """

    def _assert_model_is_valid(self):
        try:
            self.lesson_request.full_clean()
        except (ValidationError):
            self.fail('Test setup model should be valid')

    def _assert_model_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.lesson_request.full_clean()

    """
    Test cases
    """

    def test_valid_user(self):
        self._assert_model_is_valid()

    def test_interval_cannot_be_empty(self):
        self.lesson_request.interval = None
        self._assert_model_is_invalid()

    def test_duration_cannot_be_empty(self):
        self.lesson_request.duration = None
        self._assert_model_is_invalid()

    def test_quantity_cannot_be_empty(self):
        self.lesson_request.quantity = None
        self._assert_model_is_invalid()

    def test_availability_cannot_be_empty(self):
        self.lesson_request.availability = ''
        self._assert_model_is_invalid()

    def test_student_profile_cannot_be_empty(self):
        self.lesson_request.student_profile = None
        self._assert_model_is_invalid()

    def test_notes_can_be_empty(self):
        self.lesson_request.notes = None
        self._assert_model_is_valid()

    def test_short_interval_formatted_correctly(self):
        self.assertEqual(self.lesson_request.interval_formatted(), "1 week")

    def test_long_interval_formatted_correctly(self):
        self.lesson_request.interval = 2
        self.assertEqual(self.lesson_request.interval_formatted(), "2 weeks")

    def test_duration_formatted_correctly(self):
        self.assertEqual(self.lesson_request.duration_formatted(), "60 minutes")

    def test_notes_can_be_1000_chars(self):
        self.lesson_request.notes = 'A' * 1000
        self._assert_model_is_valid()

    def test_notes_cannot_be_1001_chars(self):
        self.lesson_request.notes = 'A' * 1001
        self._assert_model_is_invalid()

    def test_quantity_cannot_be_0(self):
        self.lesson_request.quantity = 0
        self._assert_model_is_invalid()

    def test_quantity_cannot_be_26(self):
        self.lesson_request.quantity = 0
        self._assert_model_is_invalid()
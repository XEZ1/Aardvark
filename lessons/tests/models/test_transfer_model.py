from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models.transfer_models import Transfer
from datetime import datetime, timedelta
from lessons.tests.helpers import *

class TransferModelTestCase(TestCase, LoginHelper, LessonHelper, SchoolTermHelper, TransferHelper):

    def setUp(self):
        self._create_student_user()
        self._create_admin_user()
        self._create_school_term()
        self._create_teacher_user()
        self._assign_lesson_request_to_user(self.student_user)
        self.lesson_request = self.student_user.student_profile.lesson_requests.first()
        self._assign_lesson_booking_to_lesson_request(self.lesson_request)
        self.lesson_booking = self.admin_user.admin_profile.lesson_bookings.first()
        self._create_transfer(self.lesson_booking)

    def _assert_model_is_valid(self):
        try:
            self.transfer.full_clean()
        except (ValidationError):
            self.fail('Test setup model should be valid')

    def _assert_model_is_invalid(self, transfer):
        with self.assertRaises(ValidationError):
            transfer.full_clean()

    def test_date_cannot_be_blank(self):
        self.transfer.date = None
        self._assert_model_is_invalid(self.transfer)

    def test_balance_cannot_be_blank(self):
        self.transfer.balance = None
        self._assert_model_is_invalid(self.transfer)

    def test_reference_cannot_be_blank(self):
        self.transfer.lesson_booking = None
        self._assert_model_is_invalid(self.transfer)

    def test_balance_must_be_lower_than_1_million(self):
        self.transfer.balance = 1000000
        self._assert_model_is_invalid(self.transfer)

    def test_balance_must_be_higher_or_equal_to_1_penny(self):
        self.transfer.balance = 0.009
        self._assert_model_is_invalid(self.transfer)

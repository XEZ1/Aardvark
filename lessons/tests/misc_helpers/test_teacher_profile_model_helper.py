from django.test import TestCase
from datetime import datetime, timedelta
from django.db import transaction
from django.contrib import messages
from lessons.view_models import TransactionViewModel
from lessons.helpers import *
from lessons.tests.helpers import *

class TeacherProfileModelHelperTestCase(TestCase, LoginHelper, LessonHelper, SchoolTermHelper, TransferHelper):
    """
    Contains the test cases for the teacher profile model helper
    """

    def setUp(self):
        """
        Simulate student's leeson booking
        """

        self._create_student_user()
        self._create_admin_user()
        self._create_school_term()
        self._create_secondary_teacher_user()
        self._create_teacher_user()
        self._assign_lesson_request_to_user(self.student_user)
        self.lesson_request = self.student_user.student_profile.lesson_requests.first()
        self._assign_lesson_booking_to_lesson_request(self.lesson_request)
        self.lesson_booking = self.admin_user.admin_profile.lesson_bookings.first()

    def test_get_bookings_for_teacher_with_booking(self):
        helper = TeacherProfileModelHelper()
        self.assertEqual(len(helper.lesson_bookings_for_teacher(self.teacher_user.teacher_profile)), 1)

    def test_get_bookings_for_teacher_without_booking(self):
        helper = TeacherProfileModelHelper()
        self.assertEqual(len(helper.lesson_bookings_for_teacher(self.teacher_user_2.teacher_profile)), 0)
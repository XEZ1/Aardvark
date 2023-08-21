from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models.term_models import SchoolTerm
from datetime import datetime, timedelta, time
from lessons.tests.helpers import SchoolTermHelper, LoginHelper, LessonHelper
from ..models import User, UserType, LessonBooking


class TeacherModelTestCase(TestCase, LoginHelper, LessonHelper, SchoolTermHelper):
    """
    Contains the test cases for the teacher user model that is used for authentication
    """
    def setUp(self):
        """
        Simulate the form input
        """
        self._create_student_user()
        self._create_teacher_user()
        self._assign_lesson_request_to_user(self.student_user)
        self._create_admin_user()
        self._create_school_term()
        self._assign_lesson_booking_to_lesson_request(self.student_user.student_profile.lesson_requests.first())
        self._log_in_as_teacher()
        self.lesson_booking = self.admin_user.admin_profile.lesson_bookings.first()
        
        self.form_input = {
            'first_name': 'JaneNew',
            'last_name' : 'DoeNew',
            'email' : 'janedoe@example.com',
            'password' : 'Password1234',
            'password_confirm' : 'Password1234' }

    """
    Test cases
    """

    def test_str_is_equal_to_teacher_full_name(self):
        """
        Check to see if teacher object is displayed as a name
        """
        self.assertEqual(str(self.teacher_user.full_name()), self.teacher_user.full_name())

    
    def test_overlap_on_dates_that_do_not_overlap(self):
        """
        Two selected dates should not overlap
        """
        # teacher lesson 1 start and end date
        date_start_1 = '2022-09-20'
        date_end_1 = '2022-09-29'

        # teacher lesson 2 start and end date
        date_start_2 = '2022-10-20'
        date_end_2 = '2022-10-29'

        self.assertEqual(self.teacher_user.teacher_profile.overlaps(date_start_1, date_end_1, date_start_2, date_end_2), False)

    def test_overlap_on_dates_that_do_overlap(self):
        """
        Two selected dates should overlap
        """
        # teacher lesson 1 start and end date
        date_start_1 = '2022-09-20'
        date_end_1 = '2022-09-29'

        # teacher lesson 2 start and end date
        date_start_2 = '2022-09-20' 
        date_end_2 = '2022-10-29'

        self.assertEqual(self.teacher_user.teacher_profile.overlaps(date_start_1, date_end_1, date_start_2, date_end_2), True)

    def test_teacher_is_available(self):
        """
        Teacher has no lessons booked on Tuesday so should be available
        """
        self.lesson_booking.regular_start_time = time(hour=9)
        self.lesson_booking.save()

        self.assertTrue(self.teacher_user.teacher_profile.is_available([self.lesson_booking], datetime.now().date(), (datetime.now() + timedelta(days=90)).date(), 'TUESDAY', time(hour=10), time(hour=11)))

    def test_teacher_is_not_available(self):
        """
        Teacher has no lessons booked on Tuesday so should be available
        """
        self.lesson_booking.regular_start_time = time(hour=9)
        self.lesson_booking.save()
        
        self.assertFalse(self.teacher_user.teacher_profile.is_available([self.lesson_booking], datetime.now().date(), (datetime.now() + timedelta(days=90)).date(), 'MONDAY', time(hour=9, minute=15), time(hour=10)))

    def test_overlap_on_times_that_do_not_overlap(self):
        """
        Two selected times should not overlap
        """
        # Timeframe 1
        time_start_1 = time(hour=12)
        time_end_1 = time(hour=14)

        # Timeframe 2
        time_start_2 = time(hour=15)
        time_end_2 = time(hour=17)

        self.assertFalse(self.teacher_user.teacher_profile.time_overlaps(time_start_1, time_end_1, time_start_2, time_end_2))

    def test_overlap_on_times_that_do_overlap(self):
        """
        Two selected times should overlap
        """
        # Timeframe 1
        time_start_1 = time(hour=12)
        time_end_1 = time(hour=14)

        # Timeframe 2
        time_start_2 = time(hour=13)
        time_end_2 = time(hour=17)

        self.assertTrue(self.teacher_user.teacher_profile.time_overlaps(time_start_1, time_end_1, time_start_2, time_end_2))
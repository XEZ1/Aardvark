from django.test import TestCase
from lessons.forms.user_forms import *
from django.urls import reverse
from ..helpers import LoginHelper, LessonHelper, SchoolTermHelper
from django.contrib import messages

class ViewLessonBookingsViewTestCase(TestCase, LoginHelper, LessonHelper, SchoolTermHelper):
    """
    Contains the test cases for the view lesson bookings view
    """

    def setUp(self):
        """
        Get routed URL
        """

        self._create_teacher_user()
        self._create_student_user()
        self._create_secondary_teacher_user()
        self._create_admin_user()
        self._create_secondary_student_user()
        self._create_school_term()
        self._assign_lesson_request_to_user(self.student_user)
        self._assign_lesson_booking_to_lesson_request(self.student_user.student_profile.lesson_requests.first())
        self._assign_lesson_request_to_user(self.student_user_2)
        self._assign_lesson_booking_to_lesson_request(self.student_user_2.student_profile.lesson_requests.first(), self.teacher_user_2)

        # It is done this way so that if URL it altered in future, test doesn't break
        self.url = reverse('view_lesson_bookings')

    """
    Test cases
    """

    def test_register_url(self):
        self.assertEqual(self.url, '/lesson-bookings/')
    
    def test_view_restricted_for_guest(self):
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_login(response)

    def test_get_lesson_bookings_for_teacher(self):
        """
        Teacher can only view lesson bookings specific to that user
        """
        # Log in as a teacher
        self._log_in_as_teacher_2()
        
        # teacher should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Should only be a single displayed lesson request - their own
        lesson_bookings_displayed = response.context['lesson_bookings']
        self.assertEqual(len(lesson_bookings_displayed), 1)
        self.assertEqual(lesson_bookings_displayed[0].teacher.user.id, self.teacher_user_2.id)

        # Check template used - should be simple one
        self.assertTemplateUsed(response, 'templates/lesson/view_lesson_bookings_extended.html')

    def test_get_lesson_bookings_for_student(self):
        # Log in as a student
        self._log_in_as_student()
        
        # Student should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Should only be a single displayed lesson request - their own
        lesson_bookings_displayed = response.context['lesson_bookings']
        self.assertEqual(len(lesson_bookings_displayed), 1)
        self.assertEqual(lesson_bookings_displayed[0].lesson_request.student_profile.user, self.student_user)

        # Check template used - should be simple one
        self.assertTemplateUsed(response, 'templates/lesson/view_lesson_bookings.html')

    def test_get_lesson_bookings_for_student_parent(self):
        # Assign student_user_2 to be the child of student_user        
        self.student_user_2.student_profile.parent = self.student_user.student_profile
        self.student_user_2.student_profile.save()

        # Log in as a student
        self._log_in_as_student()
        
        # Student should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Should only be a single displayed lesson request - their own
        lesson_bookings_displayed = response.context['lesson_bookings']
        self.assertEqual(len(lesson_bookings_displayed), 2)

        # Check template used - should be simple one
        self.assertTemplateUsed(response, 'templates/lesson/view_lesson_bookings.html')

    def test_get_lesson_bookings_for_student_child(self):
        # Assign student_user_2 to be the child of student_user        
        self.student_user_2.student_profile.parent = self.student_user.student_profile
        self.student_user_2.student_profile.save()

        self._log_in_as_student_2()
        
        # Student should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Should only be a single displayed lesson request - their own
        lesson_bookings_displayed = response.context['lesson_bookings']
        self.assertEqual(len(lesson_bookings_displayed), 1)
        self.assertEqual(lesson_bookings_displayed[0].lesson_request.student_profile.user, self.student_user_2)

        # Check template used - should be simple one
        self.assertTemplateUsed(response, 'templates/lesson/view_lesson_bookings.html')

    def test_get_lesson_bookings_for_admin(self):
        self._log_in_as_admin()
        
        # Student should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Should only be a single displayed lesson request - their own
        lesson_bookings_displayed = response.context['lesson_bookings']
        self.assertEqual(len(lesson_bookings_displayed), 2)

        # Check template used - should be simple one
        self.assertTemplateUsed(response, 'templates/lesson/view_lesson_bookings_extended.html')

    def test_get_lesson_requests_for_director(self):
        self._log_in_as_admin()

        # Student should be logged in
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        lesson_bookings_displayed = response.context['lesson_bookings']
        self.assertEqual(len(lesson_bookings_displayed), 2)

        # Check template used - should be simple one
        self.assertTemplateUsed(response, 'templates/lesson/view_lesson_bookings_extended.html')

    def test_empty_search_returns_all_requests(self):
        self._log_in_as_admin()

        response = self.client.get(self.url, search_term = '')

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # No message should appear for empty search
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 0)

        # Should only be both users lesson bookingds displayed
        lesson_bookings_displayed = response.context['lesson_bookings']
        self.assertEqual(len(lesson_bookings_displayed), 2)

    def test_search_is_not_case_sensitive(self):
        self._log_in_as_admin()

        search_data = { "search_term": "JANE DOE" }
        response = self.client.get(self.url, search_data, follow=True)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Info message should appear
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.INFO)

        # Should display 1 user
        lesson_bookings_displayed = response.context['lesson_bookings']
        self.assertEqual(len(lesson_bookings_displayed), 1)

    def test_search_checks_email(self):
        self._log_in_as_admin()

        search_data = { "search_term": "student_2@example.com" }
        response = self.client.get(self.url, search_data, follow=True)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Info message should appear
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.INFO)
        
        # Should display 1 user
        lesson_bookings_displayed = response.context['lesson_bookings']
        self.assertEqual(len(lesson_bookings_displayed), 1)

    def test_search_checks_full_name(self):
        self._log_in_as_admin()

        search_data = { "search_term": "John Doe" }
        response = self.client.get(self.url, search_data, follow=True)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Info message should appear
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.INFO)
        
        # Should display 1 user
        lesson_bookings_displayed = response.context['lesson_bookings']
        self.assertEqual(len(lesson_bookings_displayed), 1)
        self.assertEqual(lesson_bookings_displayed[0].lesson_request.student_profile.user, self.student_user_2)

    def test_search_with_no_results(self):
        self._log_in_as_admin()

        search_data = { "search_term": "No match john doe" }
        response = self.client.get(self.url, search_data, follow=True)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Error message should appear
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.ERROR)
        
        # Should display 0 user
        lesson_bookings_displayed = response.context['lesson_bookings']
        self.assertEqual(len(lesson_bookings_displayed), 0)

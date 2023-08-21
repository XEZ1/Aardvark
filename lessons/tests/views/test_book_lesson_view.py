from django.test import TestCase
from lessons.models.user_models import UserType
from lessons.models.lesson_models import AvailabilityPeriod, LessonBooking
from lessons.forms.lesson_forms import BookLessonForm
from django.urls import reverse
from ..helpers import LoginHelper, LessonHelper, SchoolTermHelper
from django.contrib import messages
from datetime import datetime, timedelta

class BookLessonViewTestCase(TestCase, LoginHelper, LessonHelper, SchoolTermHelper):
    """
    Contains the test cases for the book lesson view
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
            'school_term': self.school_term.id,
            'start_date': self.date.strftime("%Y-%m-%d"),
            'end_date': (self.date + timedelta(days=30)).strftime("%Y-%m-%d"),
            'teacher': self.teacher_user.teacher_profile.id,
            'regular_day': 'MONDAY',
            'regular_start_time': self.time,
            'interval': '1',
            'duration': '60',
            'quantity': '2', 
            }

        self.url = reverse('book_lesson', kwargs={ 'id': self.lesson_request.id })

    """
    Test cases
    """

    def test_url(self):
        self.assertEqual(self.url, f'/lesson-requests/book/{ self.lesson_request.id }/')

    def test_view_restricted_for_guest(self):
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_login(response=response)

    def test_view_restricted_for_student(self):
        self._log_in_as_student()
        self.assertTrue(self._is_logged_in())
        
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.STUDENT)

    def test_view_restricted_for_teacher(self):
        self._log_in_as_teacher()
        self.assertTrue(self._is_logged_in())
        
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response=response, dashboard_type=UserType.TEACHER)

    def test_view_available_for_director(self):
        self._create_director_user()
        self._log_in_as_director()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/lesson/book_lesson.html')

    def test_view_available_for_admin(self):
        self._log_in_as_admin()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/lesson/book_lesson.html')

    def test_renders_request_information(self):
        self._log_in_as_admin()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/lesson/book_lesson.html')
        self.assertContains(response, '<p class="underfield-label">', count=5)

    def test_book_of_non_existent_lesson_request(self):
        self._log_in_as_admin()

        before_count = LessonBooking.objects.count()
        url = reverse('book_lesson', kwargs={ 'id': 2 })
        response = self.client.post(url, follow=True)
        after_count = LessonBooking.objects.count()

        # Check no deletes have taken place
        self.assertEqual(before_count, after_count)

        # Should redirect to view page
        response_url = reverse('view_lesson_requests')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        # Should be error message on it
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(messagesList[0].level, messages.ERROR)

    def test_unsuccesful_lesson_booking(self):
        self._log_in_as_admin()
        self.assertTrue(self._is_logged_in())

        self.form_input['regular_day'] = ''

        before_count = LessonBooking.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = LessonBooking.objects.count()

        # Check no insert taken place
        self.assertEqual(before_count, after_count)

        # Check page still valid
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'templates/lesson/book_lesson.html')

        form = response.context['form']
        self.assertTrue(isinstance(form, BookLessonForm))
        self.assertTrue(form.is_bound)

        # An error message should've flagged.
        self.assertTrue(len(form.errors) >= 1)

    def test_succesful_lesson_booking(self):
        self._log_in_as_admin()
        self.assertTrue(self._is_logged_in())

        before_count = LessonBooking.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = LessonBooking.objects.count()

        # Check insert has taken place
        self.assertEqual(before_count, after_count - 1)
        
        # Check that redirect is to view lesson requests view
        response_url = reverse('view_lesson_requests')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        # A success message should've flagged.
        messagesList = list(response.context['messages'])
        self.assertTrue(len(messagesList) >= 1)
        self.assertEqual(messagesList[0].level, messages.SUCCESS)

        # Check that the fields went through to database
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
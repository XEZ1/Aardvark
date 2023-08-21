from lessons.forms.user_forms import *
from lessons.forms.lesson_forms import *
from lessons.forms.transfer_forms import *
from django.urls import reverse
from datetime import timedelta

class TransferHelper:
    """
    Contains helper methods to manage student transactions during testing
    """

    def _create_transfer(self, lesson_booking):
        """
        Creates a transfer of 250 GBP from today
        """
        self.transfer = Transfer()

        self.transfer.date = datetime.now()
        self.transfer.balance = 250
        self.transfer.lesson_booking = lesson_booking
        self.transfer.save()

class SchoolTermHelper:
    """
    Contains helper methods to manage school terms during testing
    """

    def _create_school_term(self):
        """
        Creates a school term of length 90 days from today
        """
        self.school_term = SchoolTerm()

        self.school_term.label = "Term 1"
        self.school_term.start_date = datetime.now()
        self.school_term.end_date = (datetime.now()+ timedelta(days=90))
        self.school_term.save()
        return self.school_term

    def _create_school_past_term(self):
        """
        Creates a school term of length 90 days from today
        """
        self.school_term = SchoolTerm()

        self.school_term.label = "Term 1"
        self.school_term.start_date = (datetime.now()- timedelta(days=190))
        self.school_term.end_date = (datetime.now()- timedelta(days=100))
        self.school_term.save()
        return self.school_term
    


    def _create_school_next_term(self):

        self.school_term = SchoolTerm()
        self.school_term.label = "Term 2"
        self.school_term.start_date = datetime.now()+ timedelta(days=95)
        self.school_term.end_date = (datetime.now()+ timedelta(days=95)+ timedelta(days=90))
        self.school_term.save()
        return self.school_term

class LessonHelper:
    """
    Contains helper methods to manage lessons during testing
    """

    def _assign_lesson_request_to_user(self, user):
        """
        Creates a new lesson request and assigns it to the user provided
        """
        lesson_request = LessonRequest()

        lesson_request.interval = 1
        lesson_request.quantity = 2
        lesson_request.duration = 60
        lesson_request.notes = "Test notes"
        lesson_request.availability = 'MONDAY,TUESDAY'
        lesson_request.student_profile = user.student_profile
        lesson_request.save()

    def _assign_lesson_booking_to_lesson_request(self, lesson_request, custom_teacher=None):
        """
        Assumes that self._create_admin_user() has been called before
        Assumes that self._create_teacher_user() has been called before this call
        Ensure that the school term is created first
        Creates a new lesson booking and assigns it to the lesson request
        """

        teacher = self.teacher_user.teacher_profile
        if custom_teacher:
            teacher = custom_teacher.teacher_profile
            
        lesson_booking = LessonBooking()

        lesson_booking.school_term = self.school_term
        lesson_booking.start_date = datetime.now()
        lesson_booking.end_date = datetime.now() + timedelta(days=30)
        lesson_booking.interval = 1
        lesson_booking.quantity = 2
        lesson_booking.duration = 60
        lesson_booking.teacher = teacher
        lesson_booking.regular_day = AvailabilityPeriod.MONDAY
        lesson_booking.regular_start_time = datetime.now().time()
        lesson_booking.admin_profile = self.admin_user.admin_profile
        lesson_booking.lesson_request = lesson_request
        lesson_booking.save()

class LoginHelper:
    """
    Contains the main boilerplate code for many test cases in relation to login queries.
    """

    """
    Helper methods
    """

    def _create_basic_lesson_request(self):
        """
        Will create lesson request and return it
        Does not contain student profile reference
        """

        lesson_request = LessonRequest()

        lesson_request.interval = 1
        lesson_request.quantity = 2
        lesson_request.duration = 60
        lesson_request.notes = "Test notes"
        lesson_request.availability = 'MONDAY,TUESDAY'

        return lesson_request

    """
    Assertion methods
    """

    def assert_redirected_to_login(self, response):
        """
        Asserts that a user has been redirected to the login form
        """
        # Check for redirect
        response_url = f"{ reverse('log_in') }?next={ self.url }"
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LoginUserForm))

        # Shouldn't be bound as new instance
        self.assertFalse(form.is_bound)

    def assert_redirected_to_dashboard(self, response, dashboard_type):
        """
        Asserts that a user has been redirected back to their dashboard
        """
        # Check for redirect
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        # Check template used
        if (dashboard_type == UserType.STUDENT):
            self.assertTemplateUsed(response, 'templates/student/student_dashboard.html')
        elif (dashboard_type == UserType.ADMIN):
            self.assertTemplateUsed(response, 'templates/admin/admin_dashboard.html')
        elif (dashboard_type == UserType.TEACHER):
            self.assertTemplateUsed(response, 'templates/teacher/teacher_dashboard.html')
        else:
            self.assertTemplateUsed(response, 'templates/director/director_dashboard.html')

    def assert_redirected_to_registration_page(self, response):
        """
        Asserts that a user has been redirected to registration page
        """
        # Check for redirect
        response_url = reverse('register')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        self.assertTemplateUsed(response, 'templates/student/register.html')

    def assert_redirected_to_see_children(self, response):
        """
        Asserts that a user has been redirected to see children page
        """
        # Check for redirect
        response_url = reverse('see_registered_children')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        self.assertTemplateUsed(response, 'templates/student/see_registered_children.html')

    """
    Helper methods
    """

    def _is_logged_in(self):
        """
        Checks whether current user is logged in
        This log-in test was based off the same technique shown in the intructional videos on KEATs
        """
        return '_auth_user_id' in self.client.session.keys()

    def _create_student_user(self):
        """
        Will create active student user with following credentials:
        Email: student@example.com
        Password: Password123
        """

        self.student_user = User.objects.create_user(
            'student@example.com',
            first_name='Jane',
            last_name='Doe',
            email='student@example.com',
            password='Password123',
            type=UserType.STUDENT,
            is_active=True)

        # Add empty student profile
        student_profile = StudentProfile()
        student_profile.user = self.student_user
        student_profile.save()

    def _create_child_user_for_student_user(self):
        self.student_user_child = User.objects.create_user(
            'studentChild@example.com',
            first_name='Child',
            last_name='Doe',
            email='studentChild@example.com',
            password='Password123',
            type=UserType.STUDENT,
            is_active=True)

        # Add empty student profile
        student_profile = StudentProfile()
        student_profile.user = self.student_user_child
        student_profile.save()

        self.student_user_child.student_profile.parent = self.student_user.student_profile
        self.student_user_child.student_profile.save()


    def _create_secondary_student_user(self):
        """
        Creates another student user
        """

        # Create secondary user
        self.student_user_2 = User.objects.create_user(
            'student_2@example.com',
            first_name='John',
            last_name='Doe',
            email='student_2@example.com',
            password='Password123',
            type=UserType.STUDENT,
            is_active=True)

        # Add empty student profile
        student_profile = StudentProfile()
        student_profile.user = self.student_user_2
        student_profile.save()

    def _create_teacher_user(self):
        """
        Will create active teacher user with following credentials:
        Email: teacher@example.com
        Password: Password123
        """

        self.teacher_user = User.objects.create_user(
            'teacher@example.com',
            first_name='Jane',
            last_name='Doe',
            email='teacher@example.com',
            password='Password123',
            type=UserType.TEACHER,
            is_active=True)

        # Add empty teacher profile
        teacher_profile = TeacherProfile()
        teacher_profile.user = self.teacher_user
        teacher_profile.save()

    def _create_secondary_teacher_user(self):
        """
        Creates another teacher user
        """

        # Create secondary user
        self.teacher_user_2 = User.objects.create_user(
            'teacher_2@example.com',
            first_name='John',
            last_name='Doe',
            email='teacher_2@example.com',
            password='Password123',
            type=UserType.TEACHER,
            is_active=True)

        # Add empty teacher profile
        teacher_profile = TeacherProfile()
        teacher_profile.user = self.teacher_user_2
        teacher_profile.save()

    def _create_admin_user(self):
        """
        Will create active admin user with following credentials:
        Email: admin@example.com
        Password: Password123
        """

        self.admin_user = User.objects.create_user(
            'admin@example.com',
            first_name='Jane',
            last_name='Doe',
            email='admin@example.com',
            password='Password123',
            type=UserType.ADMIN,
            is_active=True)

        # Add empty admin profile
        admin_profile = AdminProfile()
        admin_profile.user = self.admin_user
        admin_profile.save()

    def _create_director_user(self):
        """
        Will create active director user with following credentials:
        Email: director@example.com
        Password: Password123
        """
        self.director_user = User.objects.create_user(
            'director@example.com',
            first_name='Jane',
            last_name='Doe',
            email='director@example.com',
            password='Password123',
            type=UserType.DIRECTOR,
            is_active=True)

    def _log_in_as_teacher(self):
        """
        Logs in the client as a teacher.
        Assumes that the default teacher user is present within database.
        """
        if (self._is_logged_in()):
            self.client.logout()
        self.client.login(username='teacher@example.com', password='Password123')

    def _log_in_as_teacher_2(self):
        """
        Logs in the client as a teacher 2.
        Assumes that the default teacher user is present within database.
        """
        if (self._is_logged_in()):
            self.client.logout()
        self.client.login(username='teacher_2@example.com', password='Password123')

    def _log_in_as_student(self):
        """
        Logs in the client as a student.
        Assumes that the default student user is present within database.
        """
        if (self._is_logged_in()):
            self.client.logout()
        self.client.login(username='student@example.com', password='Password123')

    def _log_in_as_student_child(self):
        """
        Logs in the client as a student.
        Assumes that the default student user is present within database.
        """
        if (self._is_logged_in()):
            self.client.logout()
        self.client.login(username='studentChild@example.com', password='Password123')

    def _log_in_as_student_2(self):
        """
        Logs in the client as a student 2.
        Assumes that the default student user is present within database.
        """
        if (self._is_logged_in()):
            self.client.logout()
        self.client.login(username='student_2@example.com', password='Password123')

    def _log_in_as_admin(self):
        """
        Logs in the client as an admin.
        Assumes that the default admin user is present within database.
        """
        if (self._is_logged_in()):
            self.client.logout()
        self.client.login(username='admin@example.com', password='Password123')

    def _log_in_as_director(self):
        """
        Logs in the client as a director.
        Assumes that the default director user is present within database.
        """
        if (self._is_logged_in()):
            self.client.logout()
        self.client.login(username='director@example.com', password='Password123')

    def _log_in_as_child(self):
        """
        Logs in the client as a child.
        Assumes that the default student user is present within database.
        """
        if (self._is_logged_in()):
            self.client.logout()
        self.client.login(username='goddamnchild@example.com', password='Password123')

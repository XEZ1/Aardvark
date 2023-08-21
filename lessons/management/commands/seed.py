from django.core.management.base import BaseCommand, CommandError
from lessons.models import *
from faker import Faker
import random
from datetime import timedelta, date, datetime, time
from django.db.models import Q

class Command(BaseCommand):
    """
    Fill database with specified users
    """
    PASSWORD = "Password123"
    STUDENT_USER_COUNT = 100

    teacher_availability = {}

    def __init__(self):
        """
        Assign the Faker object and call super constructor
        """
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        """
        Create all seeding-required entities
        """
        self._create_school_terms()
        self._create_teachers()
        self._create_core_teacher()
        self._create_core_director()
        self._create_core_admins()
        self._create_core_student()
        
        student_user_count = 0
        while student_user_count < Command.STUDENT_USER_COUNT:
            try:
                self._create_student_user()
            except:
                raise
            student_user_count += 1
            print(f'Successfully seeded student user { student_user_count }')

        print("The process of seeding the database has completed successfully")

    """
    Main creation functions
    """

    def _create_core_admins(self):
        """
        Creates core seed admin
        """
        # Create admin user main
        admin_user = self._unprofiled_user("petra.pickles@example.org", UserType.ADMIN)
        admin_user.first_name = "Petra"
        admin_user.last_name = "Pickles"
        admin_user.save()

        admin_profile = AdminProfile()
        admin_profile.user = admin_user
        admin_profile.save()

        # Create admin user secondary
        admin_user_1 = self._unprofiled_user(None, UserType.ADMIN)
        admin_profile_1 = AdminProfile()
        admin_profile_1.user = admin_user_1
        admin_profile_1.save()

        print("Core school administrators seeded")

    def _create_core_director(self):
        """
        Create core seed director
        """
        # Create director user
        director_user = self._unprofiled_user("marty.major@example.org", UserType.DIRECTOR)
        director_user.first_name = "Marty"
        director_user.last_name = "Major"
        director_user.save()

        director_profile = AdminProfile()
        director_profile.user = director_user
        director_profile.save()

        print("Core school director seeded")

    def _create_core_teacher(self):
        """
        Create core seed teacher
        """
        # Create standard specified teacher
        teacher_user = self._unprofiled_user("norma.noe@example.org", UserType.TEACHER)
        teacher_user.first_name = "Norma"
        teacher_user.last_name = "Noe"
        teacher_user.save()

        profile = TeacherProfile()
        profile.user = teacher_user
        profile.save()

        Command.teacher_availability[teacher_user.teacher_profile] = { 'MONDAY': 7, 'TUESDAY': 7, 'WEDNESDAY': 7, 'THURSDAY': 7, 'FRIDAY': 7, 'SATURDAY': 7, 'SUNDAY': 7 }
        print("Core school teacher seeded")

    def _create_core_student(self):
        """
        Creates core seed student
        """
        # Create student user
        student_user = self._unprofiled_user("john.doe@example.org", UserType.STUDENT)
        student_user.first_name = "John"
        student_user.last_name = "Doe"
        student_user.save()

        student_profile = StudentProfile()
        student_profile.user = student_user
        student_profile.save()

        # Associate lesson request to user
        lesson_request = self._unassigned_lesson_request()
        lesson_request.student_profile = student_profile
        lesson_request.save()

        # Associate lesson booking to user
        admin_profile = User.objects.get(email='petra.pickles@example.org').admin_profile
        lesson_booking = self._lesson_booking(lesson_request, admin_profile, User.objects.get(email='norma.noe@example.org').teacher_profile, SchoolTerm.objects.get(label='Term one'))
        lesson_booking.save()

        # Make transfer for booking
        self._assign_repeat_bookings(student_profile)
        self._assign_transfers(student_profile, True)

        # Create child 1
        child_1 = self._unprofiled_user("alice.doe@example.org", UserType.STUDENT)
        child_1.first_name = "Alice"
        child_1.last_name = "Doe"
        child_1.save()

        student_profile_1 = StudentProfile()
        student_profile_1.user = child_1
        student_profile_1.parent = student_user.student_profile
        student_profile_1.save()

        self._assign_lesson_requests(student_profile_1)
        self._assign_lesson_bookings(student_profile_1, User.objects.get(email='norma.noe@example.org').teacher_profile)
        self._assign_repeat_bookings(student_profile_1)
        self._assign_transfers(student_profile_1, True)

        # Create child 2
        child_2 = self._unprofiled_user("bob.doe@example.org", UserType.STUDENT)
        child_2.first_name = "Bob"
        child_2.last_name = "Doe"
        child_2.save()

        student_profile_2 = StudentProfile()
        student_profile_2.user = child_2
        student_profile_2.parent = student_user.student_profile
        student_profile_2.save()

        self._assign_lesson_requests(student_profile_2)
        self._assign_lesson_bookings(student_profile_2, User.objects.filter(type=UserType.TEACHER).filter(~Q(email='norma.noe@example.org')).first().teacher_profile)
        self._assign_repeat_bookings(student_profile_2)
        self._assign_transfers(student_profile_2, True)

        print("Core school student seeded")

    def _create_student_user(self, parent=None):
        """
        Create a student user with a student profile
        If parent is specified, this student will be a child
        """
        # Create authentication model
        user = self._unprofiled_user(None, UserType.STUDENT)
        
        # Add empty student profile
        profile = StudentProfile()
        profile.user = user
        
        if (parent): 
            profile.parent = parent

        profile.save()

        # Assign lesson requests and bookings
        self._assign_lesson_requests(user.student_profile)
        self._assign_lesson_bookings(user.student_profile)
        self._assign_transfers(user.student_profile)
        self._assign_repeat_bookings(user.student_profile)

        if parent == None:
            for i in range(random.randint(0, 2)):
                self._create_student_user(user.student_profile)

    def _create_teachers(self):
        """
        Create teachers for seeder
        """
        for i in range(10):
            user = self._unprofiled_user(None, UserType.TEACHER)

            profile = TeacherProfile()
            profile.user = user
            profile.save()

            Command.teacher_availability[profile] = { 'MONDAY': 7, 'TUESDAY': 7, 'WEDNESDAY': 7, 'THURSDAY': 7, 'FRIDAY': 7, 'SATURDAY': 7, 'SUNDAY': 7 }

        print("School teachers seeded")

    def _create_school_terms(self):
        """
        Creates the default school terms as specified by the seeder
        """
        term_1 = SchoolTerm()
        term_1.label = 'Term one'
        term_1.start_date = '2022-09-01'
        term_1.end_date = '2022-10-21'

        term_2 = SchoolTerm()
        term_2.label = 'Term two'
        term_2.start_date = '2022-10-31'
        term_2.end_date = '2022-12-16'

        term_3 = SchoolTerm()
        term_3.label = 'Term three'
        term_3.start_date = '2023-01-03'
        term_3.end_date = '2023-02-10'

        term_4 = SchoolTerm()
        term_4.label = 'Term four'
        term_4.start_date = '2023-02-20'
        term_4.end_date = '2023-03-31'

        term_5 = SchoolTerm()
        term_5.label = 'Term five'
        term_5.start_date = '2023-04-17'
        term_5.end_date = '2023-05-26'

        term_6 = SchoolTerm()
        term_6.label = 'Term six'
        term_6.start_date = '2023-06-05'
        term_6.end_date = '2023-07-21'

        term_1.save()
        term_2.save()
        term_3.save()
        term_4.save()
        term_5.save()
        term_6.save()

        print("Standard school terms seeded")

    """
    Data attribute generation fields
    """

    def _unprofiled_user(self, email, user_type):
        """
        Creates a user without associating it to a profile
        """
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        if email is None:
            email = f"{first_name.lower()}.{last_name.lower()}{str(random.randint(1, 1000))}@seeded.com"

        return User.objects.create_user(
            email,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=Command.PASSWORD,
            type=user_type,
            is_active=True)

    def _assign_transfers(self, student_profile, pay_all=False):
        """
        Assign some random transfers to a students lesson bookings
        """
        lesson_bookings = list(filter(lambda lesson_booking: lesson_booking.lesson_request.student_profile.id == student_profile.id, LessonBooking.objects.all()))
        for lesson_booking in lesson_bookings:
            
            transfer = Transfer()
            transfer.date = lesson_booking.start_date_actual() + timedelta(days=random.randint(1, 14))
            
            transfer.lesson_booking = lesson_booking

            choice = random.randint(1, 5)
            if pay_all or choice <= 2:
                transfer.balance = lesson_booking.calculate_total_price()
                transfer.save()
            elif choice == 3:
                transfer.balance = lesson_booking.calculate_total_price() / 0.6
                transfer.save()
            elif choice == 4:
                transfer.balance = lesson_booking.calculate_total_price() * 1.4
                transfer.save()
    
    def _assign_lesson_bookings(self, student_profile, teacher=None):
        """
        Book a random number of the lesson requests specified
        """
        if teacher == None:
            all_teachers = list(TeacherProfile.objects.all())
            random.shuffle(all_teachers)

            teacher = all_teachers.pop(0) # Select a random teacher

        lesson_requests = student_profile.lesson_requests.all()
        lesson_requests_count = student_profile.lesson_requests.all().count()
        admin_profile = User.objects.get(email='petra.pickles@example.org').admin_profile

        for i in range(random.randint(1, lesson_requests_count - 1)):
            lesson_booking = self._lesson_booking(lesson_requests[i], admin_profile, teacher, SchoolTerm.objects.get(label='Term one'))
            lesson_booking.save()

    def _assign_repeat_bookings(self, student_profile):
        """
        Get repeats for term two
        """
        lesson_bookings = list(filter(lambda lesson_booking: lesson_booking.lesson_request.student_profile.id == student_profile.id, LessonBooking.objects.all()))
        for lesson_booking in lesson_bookings:
            # Create repeat request
            lesson_request = LessonRequest()

            lesson_request.interval = lesson_booking.lesson_request.interval
            lesson_request.quantity = lesson_booking.lesson_request.quantity
            lesson_request.duration = lesson_booking.lesson_request.duration
            lesson_request.notes = lesson_booking.lesson_request.notes
            lesson_request.availability = lesson_booking.lesson_request.availability
            lesson_request.previous_booking = lesson_booking
            lesson_request.student_profile = lesson_booking.lesson_request.student_profile
            lesson_request.save()

            # Create repeat booking
            new_lesson_booking = LessonBooking()

            new_lesson_booking.school_term = SchoolTerm.objects.get(label='Term two')
            new_lesson_booking.interval = lesson_booking.interval
            new_lesson_booking.quantity = lesson_booking.quantity
            new_lesson_booking.duration = lesson_booking.duration
            new_lesson_booking.teacher = lesson_booking.teacher
            new_lesson_booking.regular_day = lesson_booking.regular_day
            new_lesson_booking.regular_start_time = lesson_booking.regular_start_time
            new_lesson_booking.admin_profile = lesson_booking.admin_profile
            new_lesson_booking.lesson_request = lesson_request

            new_lesson_booking.save()

    def _assign_lesson_requests(self, student_profile, min=2, max=3):
        """
        Assign a random number of lesson requests to the student profile (between min and max)
        """
        for i in range(random.randint(min, max)):
            lesson_request = self._unassigned_lesson_request()
            lesson_request.student_profile = student_profile
            lesson_request.save()
        
    """
    Generate specific objects - helpers
    """
    def _random_availability_string(self):
        """
        Returns a random availability string
        """
        availability_potential = [ 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY' ]
        random.shuffle(availability_potential)
        total_selections = random.randint(1, 7)

        availability = []
        while total_selections > 0:
            availability.append(availability_potential.pop(0))
            total_selections -= 1
        
        return ','.join(availability)
    
    def _unassigned_lesson_request(self):
        """
        Generates a new lesson request randomly without assigning it to a profile.
        """
        lesson_request = LessonRequest()

        lesson_request.interval = random.randint(1, 4)
        lesson_request.quantity = random.randint(1, 25)
        lesson_request.duration = random.randint(1, 4) * 15
        lesson_request.notes = f"If possible, could I have Norma Noe as my teacher"
        lesson_request.availability = self._random_availability_string()

        return lesson_request

    def _lesson_booking(self, lesson_request, admin_profile, teacher_profile, school_term):
        """
        Creates a random lesson booking for the associated lesson request
        """
        lesson_booking = LessonBooking()

        day = lesson_request.availability_formatted_as_list()[0]
        available_time_hour = Command.teacher_availability[teacher_profile][day]
        Command.teacher_availability[teacher_profile][day] = available_time_hour + 1

        lesson_booking.school_term = school_term
        lesson_booking.interval = random.randint(1, lesson_request.interval)
        lesson_booking.quantity = random.randint(1, lesson_request.quantity)
        lesson_booking.duration = lesson_request.duration
        lesson_booking.teacher = teacher_profile
        lesson_booking.regular_day = day
        lesson_booking.regular_start_time = time(hour=available_time_hour)
        lesson_booking.admin_profile = admin_profile
        lesson_booking.lesson_request = lesson_request

        return lesson_booking
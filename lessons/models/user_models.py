from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, MaxLengthValidator
from lessons.models import *
from datetime import timedelta, time, datetime
from lessons.helpers import TimeHelper

"""
Note on 'backward' properties
To anyone looking at this code, I recommend reading the following docs:
https://docs.djangoproject.com/en/dev/topics/db/queries/#backwards-related-objects
"""

class UserType(models.TextChoices):
    """
    Defines the types of user that a derrived type could be.
    """

    STUDENT = "STUDENT", "Student"
    ADMIN = "ADMIN", "Admin"
    TEACHER = "TEACHER", "Teacher"
    DIRECTOR = "DIRECTOR", "Director"

class AvailabilityPeriod(models.TextChoices):
    """
    Defines when a student is available
    """

    MONDAY = 'MONDAY', 'Monday'
    TUESDAY = 'TUESDAY', 'Tuesday'
    WEDNESDAY = 'WEDNESDAY', 'Wednesday'
    THURSDAY = 'THURSDAY', 'Thursday'
    FRIDAY = 'FRIDAY', 'Friday'
    SATURDAY = 'SATURDAY', 'Saturday'
    SUNDAY = 'SUNDAY', 'Sunday'

class User(AbstractUser):
    """
    Base user from which all types of user are derrived from.
    Model is used for authentication purposes.
    """

    username = models.EmailField(unique=True, blank=False)
    type = models.CharField(max_length=50, choices=UserType.choices, default=UserType.STUDENT)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)

    def full_name(self):
        """
        Returns the user's full name
        """
        return f"{ self.first_name } { self.last_name }"

    """
    Overridden methods
    """

    def clean(self):
        """
        Perform model validation checks that occur across multiple fields
        Docs for model validation: https://docs.djangoproject.com/en/4.1/ref/models/instances/#django.db.models.Model.clean
        """

        """
        This validation check will only occur if both the email and username fields have been populated.
        This is to prevent the a form.is_valid() calling clean too early, resulting in a crash
        """
        if (self.username and self.email and self.username != self.email):
            raise ValidationError("Username field must be equal to email field at all times")

        if (self.type is None):
            raise ValidationError("A user must be associated to a user type")

class StudentProfile(models.Model):
    """
    Represents a student with privileges to request lessons, access invoices, and other basic tasks.
    Guests can register as a student via public site.
    """

    # Represents the unique student identifer number
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField('lessons.User', on_delete=models.CASCADE, related_name="student_profile")
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE, related_name="children")

    def __str__(self):
        """
        So that objects can be printed as full full_name
        """
        return self.user.full_name()

    def is_child(self):
        """
        Checks to see if this profile is a child
        """
        return self.parent != None

    def is_parent(self):
        """
        Checks to see if this profile has children
        """
        return self.children.all().count() != 0

class AdminProfile(models.Model):
    """
    Represents an admin with much wider privileges and the ability to book lessons.
    Both directors and admins have these profiles
    """

    # Represents the unique admin identifer number
    id = models.AutoField(primary_key=True)
    
    # Foreign key
    user = models.OneToOneField('lessons.User', on_delete=models.CASCADE, related_name="admin_profile", blank=False)

class TeacherProfile(models.Model):
    """
    Represents a teacher who can book and fulfil lessons
    """

    # Represents the unique admin identifer number
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile", blank=False)

    def __str__(self):
        """
        Display a teacher object as a name
        """
        return self.user.full_name()
    
    def overlaps(self, date1_start, date1_end, date2_start, date2_end):
        """
        Checks to see if two dates overlap
        """
        return date1_start <= date2_end and date2_start <= date1_end

    def time_overlaps(self, lesson_start_time, lesson_end_time, lesson2_start_time, lesson2_end_time):
        """
        lesson_start_time -> potential start time checking
        lesson_end_time -> potential end time checking
        lesson2_start_time -> potential start time checking for lesson 2
        lesson2_end_time -> potential end time checking for lesson 2
        """
        return lesson_start_time <= lesson2_end_time and lesson2_start_time <= lesson_end_time
    
    def is_available(self, lesson_bookings, start_date, end_date, day, start_time, end_time):
        """
        Determines whether a teacher is free within a certain time period
        """
        for lesson_booking in lesson_bookings:
            time_conflict = self.time_overlaps(lesson_booking.regular_start_time, lesson_booking.end_time(), start_time, end_time)
            # Get lesson booking start and end dates or term equivs
            if self.overlaps(start_date, end_date, lesson_booking.start_date_actual(), lesson_booking.end_date_actual()) and lesson_booking.regular_day == day and time_conflict:
                return False
            
        return True
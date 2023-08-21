from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, MaxLengthValidator
from .user_models import AvailabilityPeriod
from lessons.helpers import TransactionModelHelper, TimeHelper
from datetime import timedelta

"""
Note on 'backward' properties
To anyone looking at this code, I recommend reading the following docs:
https://docs.djangoproject.com/en/dev/topics/db/queries/#backwards-related-objects
"""

REPEAT_CHOICES = (
        (1, "One term"),
        (2, "Two terms"),
        (3, "Three terms"),
        (4, "Four terms"),
        (4, "Five terms")
    )

DURATION_CHOICES = (
        (15, "15 minutes"),
        (30, "30 minutes"),
        (45, "45 minutes"),
        (60, "60 minutes")
    )

INTERVAL_CHOICES = (
    (1, "Every week"),
    (2, "Every two weeks"),
    (3, "Every three weeks"),
    (4, "Every four weeks")
)

class LessonRequest(models.Model):
    """
    Represents a request for a specific set of lessons
    """

    id = models.AutoField(primary_key=True)
    duration = models.IntegerField(choices=DURATION_CHOICES, default=60, blank=False)
    quantity = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(25)], blank=False)
    interval = models.IntegerField(choices=INTERVAL_CHOICES, default=1, blank=False)
    notes = models.TextField(blank=True, validators=[MaxLengthValidator(1000)])
    availability = models.CharField(max_length=100, blank=False)

    # If someone deletes their user profile, their requests should be deleted too.
    student_profile = models.ForeignKey('lessons.StudentProfile', on_delete=models.CASCADE, related_name="lesson_requests", blank=False)
    previous_booking = models.OneToOneField('lessons.LessonBooking', on_delete=models.SET_NULL, blank=True, null=True)

    def availability_formatted(self):
        """
        Returns the availability in a freindly format (without capitals and with spaces)
        """
        new_availability = []
        for day in self.availability.split(','):
            day = day[:1].upper() + day[1:].lower()
            new_availability.append(day)
        return ", ".join(new_availability)

    def availability_formatted_as_list(self):
        """
        Returns the availability as a list
        """
        return self.availability.split(',')

    def duration_formatted(self):
        """
        Returns the duration in a nice format
        """
        return f"{self.duration} minutes"

    def interval_formatted(self):
        """
        Returns the interval in a nice format
        """
        if (self.interval == 1):
            return "1 week"
        else:
            return f"{self.interval} weeks"

    def status(self):
        """
        Checks to see if the request has been booked or not
        """
        if hasattr(self, 'lesson_booking'):
            return "Fulfilled"
        else:
            return "Unfulfilled"

    """
    Overridden methods
    """

    def clean(self):
        """
        Cross-field validation tests
        """

        if self.availability == None:
            raise ValidationError("Availability must be provided for a lesson request")

class LessonBooking(models.Model):
    """
    Represent a book lesson that has been generated through a request
    """

    """
    Class variables

    Epic 1 simply wanted a price calculated and nothing more.
    Due to this, prices are simply stored in class variables for this version
    """
    # The rate that is applied by default to every lesson, irrespective of duration
    LESSON_PRICE = 5

    """
    Model fields
    """

    id = models.AutoField(primary_key=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    regular_start_time = models.TimeField(blank=False, null=False)
    regular_day = models.CharField(max_length=100,choices=AvailabilityPeriod.choices, blank=False)
    duration = models.IntegerField(choices=DURATION_CHOICES, default=60, blank=False)
    quantity = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(25)], blank=False)
    interval = models.IntegerField(choices=INTERVAL_CHOICES, default=1, blank=False)

    # Navigation properties
    lesson_request = models.OneToOneField('lessons.LessonRequest', on_delete=models.CASCADE, related_name="lesson_booking", blank=False)
    admin_profile = models.ForeignKey('lessons.AdminProfile', on_delete=models.SET_NULL, related_name="lesson_bookings", blank=True, null=True)
    school_term = models.ForeignKey('lessons.SchoolTerm', on_delete=models.CASCADE, related_name="lesson_bookings", blank=False, null=False)
    teacher = models.ForeignKey('lessons.TeacherProfile', on_delete=models.CASCADE, related_name="lesson_bookings", blank=False, null=False)

    def end_time(self):
        """
        Returns the time that the lesson ends
        """
        helper = TimeHelper()
        return helper.add_minutes_to_time(self.regular_start_time, self.duration)
        
    def invoice_number(self):
        """
        Returns the invoice number for this bookings
        """
        return f'{str(self.lesson_request.student_profile.id).rjust(4, "0")}-{str(self.id).rjust(3, "0")}'

    def start_date_actual(self):
        """
        If start_date is None, will return term start_date
        """
        if self.start_date:
            return self.start_date
        else:
            return self.school_term.start_date

    def end_date_actual(self):
        """
        If end_date is None, will return term end_date
        """
        if self.end_date:
            return self.end_date
        else:
            return self.school_term.end_date

    def calculate_total_price(self):
        """
        Calculates the price of booking the lesson schedule, accounting for quantity
        """
        return LessonBooking.LESSON_PRICE * self.quantity

    def formatted_total_price(self):
        """
        Formats the calculated total price
        """
        helper = TransactionModelHelper()
        return helper.format_to_currency(self.calculate_total_price())

    def duration_formatted(self):
        """
        Returns the duration in a nice format
        """
        return f"{self.duration} minutes"

    def interval_formatted(self):
        """
        Returns the interval in a nice format
        """
        if (self.interval == 1):
            return "1 week"
        else:
            return f"{self.interval} weeks"

    def regular_day_formatted(self):
        """
        Returns the day in formatted form.
        """
        return self.regular_day[:1].upper() + self.regular_day[1:].lower()

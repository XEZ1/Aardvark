from django import forms
from ..models import User, UserType, StudentProfile, LessonRequest, AvailabilityPeriod, LessonBooking
from django.core.validators import RegexValidator
from django.core.exceptions import FieldDoesNotExist
from django.forms import DateInput, TimeField
from datetime import datetime, timedelta
from lessons.models.term_models import SchoolTerm
from django.db.models import Q
from lessons.helpers import TimeHelper

class RequestLessonForm(forms.ModelForm):
    """
    The form used to create a new lesson request
    """
    def __init__(self, user=None, previous_booking=None, *args, **kwargs):
        """
        Dynamically populates choices and sets user
        """
        super().__init__(*args, **kwargs)
        self.previous_booking = previous_booking
        self.user = user

        # Add options for lesson request recipient
        recipient_choices = []
        recipient_choices.append((self.user.student_profile.id, "Myself"))

        for child in self.user.student_profile.children.all():
            recipient_choices.append((child.id, child.user.full_name))

        self.fields['recipient_profile_id'].choices = recipient_choices

    class Meta():
        """
        Select model fields that will be used within form.
        """
        model = LessonRequest
        fields = [ 'interval', 'quantity', 'duration', 'notes' ]
        labels = {
            'interval': 'How often would you like a lesson?',
            'quantity': 'How many lessons would you like?',
            'duration': "How long would you like each of your lessons to be?",
            'notes': "Do you have any additional requests for your lessons? (e.g., specific teacher you have worked with before)",
        }

    # Django docs: https://docs.djangoproject.com/en/4.1/ref/forms/api/#django.forms.Form.field_order
    field_order = [ 'recipient_profile_id', 'interval', 'quantity', 'duration', 'notes', 'availability' ]

    availability = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=AvailabilityPeriod.choices, required=True)
    recipient_profile_id = forms.ChoiceField(label="Who would you like to request a lesson for?")

    def clean_availability(self):
        """
        Availability is stored as CSV list
        Doesn't break normalisaton rules as entries are fixed and have no other associations
        """
        super().clean()
        return ','.join(self.cleaned_data.get('availability'))

    def save(self):
        """
        Create a new LessonRequest model and save it to the database
        """
        super().save(commit=False)
        if (self.user == None):
            raise FieldDoesNotExist('User not provided so cannot save less request')

        lesson_request = LessonRequest()

        lesson_request.previous_booking = self.previous_booking
        lesson_request.interval = self.cleaned_data.get('interval')
        lesson_request.quantity = self.cleaned_data.get('quantity')
        lesson_request.duration = self.cleaned_data.get('duration')
        lesson_request.notes = self.cleaned_data.get('notes')
        lesson_request.availability = self.cleaned_data.get('availability')
        lesson_request.student_profile = StudentProfile.objects.get(pk = self.cleaned_data.get('recipient_profile_id'))
        lesson_request.save()

class UpdateLessonRequestForm(forms.ModelForm):
    """
    The form used to update an existing lesson request
    """

    class Meta():
        """
        Select model fields that will be used within form.
        """
        model = LessonRequest
        fields = [ 'interval', 'quantity', 'duration', 'notes' ]
        labels = {
            'interval': 'How often would you like a lesson?',
            'quantity': 'How many lessons would you like?',
            'duration': "How long would you like each of your lessons to be?",
            'notes': "Do you have any additional requests for your lessons? (e.g., specific teacher you have worked with before)",
        }

    availability = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=AvailabilityPeriod.choices, required=True)

    def clean_availability(self):
        """
        Availability is stored as CSV list
        Doesn't break normalisaton rules as entries are fixed and have no other associations
        """
        super().clean()
        return ','.join(self.cleaned_data.get('availability'))

    def save(self):
        """
        Create a new LessonRequest model and save it to the database
        """
        super().save(commit=False)

        lesson_request = self.instance

        lesson_request.interval = self.cleaned_data.get('interval')
        lesson_request.quantity = self.cleaned_data.get('quantity')
        lesson_request.duration = self.cleaned_data.get('duration')
        lesson_request.notes = self.cleaned_data.get('notes')
        lesson_request.availability = self.cleaned_data.get('availability')

        lesson_request.save()

class BookLessonForm(forms.ModelForm):
    """
    The form used to book a lesson
    """

    def __init__(self, user, lesson_request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.lesson_request = lesson_request

    class Meta():
        """
        Select model fields that will be used within form.
        """
        model = LessonBooking
        fields = [ 'school_term', 'start_date', 'end_date', 'teacher', 'regular_start_time', 'regular_day',
                'duration', 'quantity', 'interval' ]

        labels = {
            'school_term': 'What term will the lesson take place in?',
            'start_date': 'When will the booked lessons start? (if unspecified, term start)',
            'end_date': 'When will the booked lessons end? (if unspecified, term end)',
            'teacher': 'What teacher will be assigned to the lessons?',
            'regular_start_time': 'What time will the lesson start?',
            'regular_day': 'What day of the week will the lesson be on?',
            'interval': 'How often will the lessons be?',
            'quantity': 'How many lessons will there be?',
            'duration': "How long will each of the lessons be?",
        }

        widgets = {
            'start_date': forms.DateInput(),
            'end_date': forms.DateInput(),
            'regular_start_time': forms.TimeInput(),
        }

    def clean(self):
        """
        Multi field validation checks
        """
        super().clean()
        helper = TimeHelper()

        quantity = self.cleaned_data.get('quantity')
        school_term = self.cleaned_data.get('school_term')
        interval = self.cleaned_data.get('interval')
        teacher = self.cleaned_data.get('teacher')
        duration = self.cleaned_data.get('duration')
        day = self.cleaned_data.get('regular_day')
        start_time = self.cleaned_data.get('regular_start_time')
        end_time = helper.add_minutes_to_time(start_time, duration)

        end_date = self.cleaned_data.get('end_date')
        if end_date is None:
             end_date = school_term.end_date

        start_date = self.cleaned_data.get('start_date')
        if start_date is None:
            start_date = school_term.start_date

        if teacher and school_term and not teacher.is_available(LessonBooking.objects.filter(teacher=teacher), start_date, end_date, day, start_time, end_time):
            self.add_error('teacher', 'The selected teacher is not available at the given time')

        if start_date < datetime.today().date():
            self.add_error('start_date', 'The lesson start date cannot be in the past')

        if not (self.cleaned_data.get('regular_day') in self.lesson_request.availability_formatted_as_list()):
            self.add_error('regular_day', 'Student is not available on the day selected')

        if quantity > self.lesson_request.quantity:
            self.add_error('quantity', 'Cannot book in more lessons that the student has requested')

        if duration > self.lesson_request.duration:
            self.add_error('duration', 'Cannot book in longer lessons than the student has requested')

        #date range cannot be outside of term time
        if school_term and (end_date > school_term.end_date or end_date < school_term.start_date):
            self.add_error('end_date', 'Schedule end date must be within term time')

        if start_date and end_date <= start_date:
            self.add_error('end_date', 'Schedule end date must be greater than start date')

        if school_term and interval:
            max_lessons = school_term.max_amount_of_lessons(interval, start_date, end_date)
            #quantity of lessons has to be within reach of interval
            if quantity > max_lessons:
                    self.add_error('quantity', f'With the interval and date range provided, a maximum of {max_lessons} lessons can be booked')

        if school_term and not (start_date >= school_term.start_date and start_date <= school_term.end_date):
            self.add_error('start_date', 'Schedule start date must be within term time')

    def save(self):
        """
        Create a new LessonRequest model and save it to the database
        """
        super().save(commit=False)

        lesson_booking = LessonBooking()

        lesson_booking.teacher = self.cleaned_data.get('teacher')
        lesson_booking.school_term = self.cleaned_data.get('school_term')
        lesson_booking.start_date = self.cleaned_data.get('start_date')
        lesson_booking.end_date = self.cleaned_data.get('end_date')
        lesson_booking.regular_start_time = self.cleaned_data.get('regular_start_time')
        lesson_booking.regular_day = self.cleaned_data.get('regular_day')
        lesson_booking.interval = self.cleaned_data.get('interval')
        lesson_booking.quantity = self.cleaned_data.get('quantity')
        lesson_booking.duration = self.cleaned_data.get('duration')
        lesson_booking.admin_profile = self.user.admin_profile
        lesson_booking.lesson_request = self.lesson_request

        lesson_booking.save()

class UpdateLessonBookingForm(forms.ModelForm):
    """
    The form used to update a lesson booking
    """

    class Meta():
        """
        Select model fields that will be used within form.
        """
        model = LessonBooking
        fields = [ 'school_term', 'start_date', 'end_date', 'teacher', 'regular_start_time', 'regular_day',
              'duration', 'quantity', 'interval' ]

        labels = {
            'school_term': 'What term will the lesson take place in?',
            'start_date': 'When will the booked lessons start? (if unspecified, term start)',
            'end_date': 'When will the booked lessons end? (if unspecified, term end)',
            'teacher': 'What teacher will be assigned to the lessons?',
            'regular_start_time': 'What time will the lesson start?',
            'regular_day': 'What day of the week will the lesson be on?',
            'interval': 'How often will the lessons be?',
            'quantity': 'How many lessons will there be?',
            'duration': "How long will each of the lessons be?",
        }

        widgets = {
            'start_date': forms.DateInput(),
            'end_date': forms.DateInput(),
            'regular_start_time': forms.TimeInput(),
        }

    def clean(self):
        """
        Multi field validation checks
        """
        super().clean()
        helper = TimeHelper()

        quantity = self.cleaned_data.get('quantity')
        school_term = self.cleaned_data.get('school_term')
        interval = self.cleaned_data.get('interval')
        teacher = self.cleaned_data.get('teacher')
        duration = self.cleaned_data.get('duration')
        day = self.cleaned_data.get('regular_day')
        start_time = self.cleaned_data.get('regular_start_time')
        end_time = helper.add_minutes_to_time(start_time, duration)

        end_date = self.cleaned_data.get('end_date')
        if end_date is None:
             end_date = school_term.end_date

        start_date = self.cleaned_data.get('start_date')
        if start_date is None:
            start_date = school_term.start_date

        if teacher and school_term and not teacher.is_available(LessonBooking.objects.filter(teacher=teacher).filter(~Q(id=self.instance.id)), start_date, end_date, day, start_time, end_time):
            self.add_error('teacher', 'The selected teacher is not available at the given time')

        if start_date < datetime.today().date():
            self.add_error('start_date', 'The lesson start date cannot be in the past')

        if not (self.cleaned_data.get('regular_day') in self.instance.lesson_request.availability_formatted_as_list()):
            self.add_error('regular_day', 'Student is not available on the day selected')

        if quantity > self.instance.lesson_request.quantity:
            self.add_error('quantity', 'Cannot book in more lessons that the student has requested')

        if duration > self.instance.lesson_request.duration:
            self.add_error('duration', 'Cannot book in longer lessons than the student has requested')

        #date range cannot be outside of term time
        if school_term and (end_date > school_term.end_date or end_date < school_term.start_date):
            self.add_error('end_date', 'Schedule end date must be within term time')

        if end_date <= start_date:
            self.add_error('end_date', 'Schedule end date must be greater than start date')

        if school_term and interval:
            max_lessons = school_term.max_amount_of_lessons(self.cleaned_data.get('interval'), start_date, end_date)
            #quantity of lessons has to be within reach of interval
            if quantity > max_lessons:
                    self.add_error('quantity', f'With the interval and date range provided, a maximum of {max_lessons} lessons can be booked')

        if school_term and not (start_date >= school_term.start_date and start_date <= school_term.end_date):
            self.add_error('start_date', 'Schedule start date must be within term time')

    def save(self):
        """
        Update bound lesson booking instance
        """
        super().save(commit=False)

        lesson_booking = self.instance

        lesson_booking.teacher = self.cleaned_data.get('teacher')
        lesson_booking.school_term = self.cleaned_data.get('school_term')
        lesson_booking.start_date = self.cleaned_data.get('start_date')
        lesson_booking.end_date = self.cleaned_data.get('end_date')
        lesson_booking.regular_start_time = self.cleaned_data.get('regular_start_time')
        lesson_booking.regular_day = self.cleaned_data.get('regular_day')
        lesson_booking.interval = self.cleaned_data.get('interval')
        lesson_booking.quantity = self.cleaned_data.get('quantity')
        lesson_booking.duration = self.cleaned_data.get('duration')

        lesson_booking.save()

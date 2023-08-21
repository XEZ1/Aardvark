from django import forms
from ..models import User, UserType, StudentProfile, SchoolTerm, AvailabilityPeriod, LessonBooking
from django.core.validators import RegexValidator
from django.core.exceptions import FieldDoesNotExist
from django.forms import DateInput, TimeField
from datetime import datetime
from django.db.models import Q

class RegisterSchoolTermForm(forms.ModelForm):
    """
    The form used to create term
    """

    class Meta():
        """
        Select model fields that will be used within form.
        """
        model = SchoolTerm
        fields = [ 'label', 'start_date', 'end_date' ]
        labels = {
            'label': 'What is the name for this term? (e.g., Term 1)',
            'start_date': "When would you like the term start date to be?",
            'end_date': "When would you like the term end date to be?",
        }
        widgets = {
            'start_date': forms.DateInput(),
            'end_date': forms.DateInput(),
        }

    def save(self):
        """
        Create a new SchoolTerm model and save it to the database
        """
        super().save(commit=False)

        term_request = SchoolTerm()

        term_request.label = self.cleaned_data.get('label')
        term_request.start_date = self.cleaned_data.get('start_date')
        term_request.end_date = self.cleaned_data.get('end_date')
        term_request.save()

    def clean(self):
        super().clean()

        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')

        #check that start_date is before end_date
        if start_date >= end_date:
            self.add_error("start_date","A term's start date has to be before its' end date")
        
        #check that term doesn't overlap with other terms 
        school_terms = SchoolTerm.objects.all()
        
        for term in school_terms:
            if start_date <= term.end_date and end_date >= term.start_date:
                self.add_error("start_date","The date range you selected clashes with another term")
                break

class UpdateSchoolTermForm(forms.ModelForm):
    """
    The form used to update term
    """

    class Meta():
        """
        Select model fields that will be used within form.
        """
        model = SchoolTerm
        fields = [ 'label',  'start_date', 'end_date' ]
        labels = {
            'label': 'What is the name for this term? (e.g., Term 1)',
            'start_date': "When would you like the term start date to be?",
            'end_date': "When would you like the term end date to be?",
        }
        widgets = {
            'start_date': forms.DateInput(),
            'end_date': forms.DateInput(),
        }

    def save(self):
        """
        Update a new SchoolTerm model and save it to the database
        """
        super().save(commit=False)

        term = self.instance

        term.label = self.cleaned_data.get('label')
        term.start_date = self.cleaned_data.get('start_date')
        term.end_date = self.cleaned_data.get('end_date')
        term.save()

    def clean(self):
        super().clean()

        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')

        #check that start_date is before end_date
        if start_date >= end_date:
            self.add_error("start_date","A term's start date has to be before its' end date")
        
        #check that term doesn't overlap with other terms
        #for kafis reference, i used https://docs.djangoproject.com/en/4.1/topics/db/queries/#complex-lookups-with-q-objects 
        school_terms = SchoolTerm.objects.filter(~Q(id=self.instance.id))
        
        for term in school_terms:
            if start_date <= term.end_date and end_date >= term.start_date:
                self.add_error("start_date","The date range you selected clashes with another term")
                break
            
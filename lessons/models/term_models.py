from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, MaxLengthValidator
from datetime import datetime
from datetime import timedelta
from datetime import date

class SchoolTerm(models.Model):

    id = models.AutoField(primary_key=True)
    label = models.CharField(unique=True, blank=False, max_length=50)
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)

    def __str__(self):
        """
        makes it so that the label is displayed on a mapped form
        conversions: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
        """
        return self.label + ' (' + self.start_date.strftime("%d/%m/%Y") + ' - ' + self.end_date.strftime("%d/%m/%Y") + ')'

    def max_amount_of_lessons(self, interval_in_weeks, start_date = None, end_date = None):
        """
        calculates the maxium amount of lessons that can be had from a date to end of term
        """
        if start_date is None:
            #if no start date provided, use the term start
            start_date = self.start_date

        if end_date is None:
            #if no end date provided, use the term end
            end_date = self.end_date

        day_diff = end_date - start_date

        #floor division
        #1 is added as start date is inclusive
        return 1+ day_diff.days // (interval_in_weeks * 7)
    
    def overlaps(self, date1_start, date1_end, date2_start, date2_end):
        """
        Checks to see if two dates overlap
        """
        return date1_start <= date2_end and date2_start <= date1_end

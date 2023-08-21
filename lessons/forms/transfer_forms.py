from django import forms
from ..models import User, UserType, StudentProfile, AdminProfile, Transfer, LessonBooking
from django.core.validators import RegexValidator
from datetime import datetime

class RegisterTransferForm(forms.ModelForm):
    """
    Can be used by the user to register a bank transfer
    """

    class Meta:
        """
        Select model fields that will be used within form.
        """
        model = Transfer
        fields = [ 'date', 'balance' ]

    invoice_ref_no = forms.CharField(label='Invoice reference number', max_length=10)

    def clean(self):
        """
        Checks that the lesson booking exists.
        """
        super().clean()

        if self.cleaned_data.get('date') > datetime.now().date():
            self.add_error('date', 'The transfer date must not be in the future')

        lesson_bookings_with_ref = list(filter(lambda booking: booking.invoice_number() == self.cleaned_data.get('invoice_ref_no'), LessonBooking.objects.all()))
        if len(lesson_bookings_with_ref) == 0:
            self.add_error('invoice_ref_no', 'No invoice associated with that reference number')
        else:
            self.cleaned_data['invoice_ref_no'] = lesson_bookings_with_ref[0]

    def save(self):
        """
        Registers the bank transfer
        """
        super().save(commit=False)

        transfer = Transfer()
        transfer.date = self.cleaned_data.get('date')
        transfer.balance = self.cleaned_data.get('balance')
        transfer.lesson_booking = self.cleaned_data.get('invoice_ref_no')
        transfer.save()

        return transfer

from django.test import TestCase
from lessons.models.user_models import UserType
from django.urls import reverse
from datetime import datetime, timedelta
from ..helpers import *

class RegisterTransferFormTestCase(TestCase, LoginHelper, LessonHelper, SchoolTermHelper, TransferHelper):
    """
    Contains the test cases for the school transfer registration form
    """

    def setUp(self):
        """
        Simulate the form input
        """

        self._create_student_user()
        self._create_admin_user()
        self._create_school_term()
        self._create_teacher_user()
        self._assign_lesson_request_to_user(self.student_user)
        self.lesson_request = self.student_user.student_profile.lesson_requests.first()
        self._assign_lesson_booking_to_lesson_request(self.lesson_request)
        self.lesson_booking = self.admin_user.admin_profile.lesson_bookings.first()

        self.form_input = {
            'date': '2022-01-01',#yyyy-mm-dd
            'balance' : 250,
            'invoice_ref_no': self.lesson_booking.invoice_number()
        }

    """
    Test cases
    """

    def test_valid_form(self):
        form = RegisterTransferForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = RegisterTransferForm()

        # Check that invoice_ref field is present
        self.assertIn('invoice_ref_no', form.fields)

        # Check that other fields are within form
        self.assertIn('balance', form.fields)
        balance_field = form.fields['balance']
        self.assertTrue(isinstance(balance_field, forms.DecimalField))

        self.assertIn('date', form.fields)
        date_field = form.fields['date']
        self.assertTrue(isinstance(date_field, forms.DateField))

    def test_form_uses_model_validation(self):
        self.form_input['invoice_ref_no'] = ''
        form = RegisterTransferForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_date_must_not_be_in_the_future(self):
        self.form_input['date'] = (datetime.now() + timedelta(days=1))
        form = RegisterTransferForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_invoice_ref_must_correspond_to_booking(self):
        self.form_input['invoice_ref_no'] = '9999-999'
        form = RegisterTransferForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_balance_must_not_be_lower_than_one_penny(self):
        self.form_input['balance'] = 0.009
        form = RegisterTransferForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = RegisterTransferForm(data=self.form_input)

        before_transfer_count = Transfer.objects.count()
        form.save()
        after_transfer_count = Transfer.objects.count()

        self.assertEqual(before_transfer_count, after_transfer_count - 1)

        transfer = Transfer.objects.get(date = '2022-01-01')

        self.assertEqual(transfer.date.strftime("%Y-%m-%d"), '2022-01-01')
        self.assertEqual(transfer.balance, 250)
        self.assertEqual(transfer.lesson_booking.id, self.lesson_booking.id)

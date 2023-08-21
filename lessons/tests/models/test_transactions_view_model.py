from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models.transfer_models import Transfer
from datetime import datetime, timedelta
from lessons.tests.helpers import *
from lessons.helpers import *
from lessons.view_models import *

class TransactionViewModelTestCase(TestCase, LoginHelper, LessonHelper, SchoolTermHelper, TransferHelper):

    def setUp(self):
        """
        Creates two different TransactionViewModel objects
        """

        self._create_student_user()
        self._create_admin_user()
        self._create_school_term()
        self._create_teacher_user()
        self._assign_lesson_request_to_user(self.student_user)
        self.lesson_request = self.student_user.student_profile.lesson_requests.first()
        self._assign_lesson_booking_to_lesson_request(self.lesson_request)
        self.lesson_booking = self.admin_user.admin_profile.lesson_bookings.first()

        # Create second transfer before the booking
        self.transfer = Transfer()
        self.transfer.date = datetime.now().date()
        self.transfer.balance = 700
        self.transfer.lesson_booking = self.lesson_booking
        self.transfer.save()

        self.transfer_transactions_view = TransactionViewModel(transfer=self.transfer)
        self.lesson_booking_transactions_view = TransactionViewModel(lesson_booking=self.lesson_booking)

    """
    Test cases
    """

    def test_transfer_transactions_view_has_necessary_fields(self):

        # Check that date field is present
        self.assertEqual(self.transfer_transactions_view.date, self.transfer.date)
        # Check that fee field is present
        self.assertEqual(self.transfer_transactions_view.fee, self.transfer.balance)
        # Check that reference field is present
        self.assertEqual(self.transfer_transactions_view.reference, "Payment")
        # Check that student field is present
        self.assertEqual(self.transfer_transactions_view.student, self.transfer.lesson_booking.lesson_request.student_profile)

    def test_lesson_booking_transactions_view_has_necessary_fields(self):

        # Check that date field is present
        self.assertEqual(self.lesson_booking_transactions_view.date, self.lesson_booking.start_date_actual())
        # Check that fee field is present
        self.assertEqual(self.lesson_booking_transactions_view.fee, self.lesson_booking.calculate_total_price() * -1)
        # Check that reference field is present
        self.assertEqual(self.lesson_booking_transactions_view.reference, self.lesson_booking.invoice_number())
        # Check that booking field is present
        self.assertEqual(self.lesson_booking_transactions_view.lesson_booking, self.lesson_booking)
        # Check that student field is present
        self.assertEqual(self.lesson_booking_transactions_view.student, self.lesson_booking.lesson_request.student_profile)

    def test_formatted_fee_returns_right_format(self):

        # Formatted fee for transafer transactions view
        self.assertEqual(self.transfer_transactions_view.formatted_fee, "700.00 GBP")
        # Formatted fee for lesson booking transactions view
        self.assertEqual(self.lesson_booking_transactions_view.formatted_fee, "-10.00 GBP")

    def test_formatted_balance_returns_right_format(self):

        transaction_helper = TransactionModelHelper()
        transfer = TransactionViewModel(transfer=self.transfer)
        booking = TransactionViewModel(lesson_booking=self.lesson_booking)
        transactions = transaction_helper.assign_balances([transfer, booking])

        # Formatted fee for transafer transactions view
        self.assertEqual(transfer.formatted_balance, "690.00 GBP")
        self.assertEqual(booking.formatted_balance, "690.00 GBP")

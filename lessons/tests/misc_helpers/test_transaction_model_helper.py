from django.test import TestCase
from datetime import datetime, timedelta
from django.db import transaction
from django.contrib import messages
from lessons.view_models import TransactionViewModel
from lessons.helpers import *
from lessons.tests.helpers import *

class TransactionModelHelperTestCase(TestCase, LoginHelper, LessonHelper, SchoolTermHelper, TransferHelper):
    """
    Contains the test cases for the transaction model helper
    """

    def setUp(self):
        """
        Simulate student's leeson booking and transactions
        """

        self._create_student_user()
        self._create_admin_user()
        self._create_school_term()
        self._create_teacher_user()
        self._assign_lesson_request_to_user(self.student_user)
        self.lesson_request = self.student_user.student_profile.lesson_requests.first()
        self._assign_lesson_booking_to_lesson_request(self.lesson_request)
        self.lesson_booking = self.admin_user.admin_profile.lesson_bookings.first()
        self._create_transfer(self.lesson_booking)

        # Create second transfer before the booking
        self.transfer = Transfer()
        date = '2020-01-01'
        self.transfer.date = datetime.strptime(date, "%Y-%m-%d")
        self.transfer.balance = 250
        self.transfer.lesson_booking = self.lesson_booking
        self.transfer.save()

        self.student_helper = StudentProfileModelHelper()
        self.transaction_helper = TransactionModelHelper()

        self.student_profile = self.student_user.student_profile

        self.transfers = list(map(lambda pr_transfer: TransactionViewModel(transfer=pr_transfer), self.student_helper.transfers_for_student(self.student_profile)))
        self.lesson_bookings = list(map(lambda pr_booking: TransactionViewModel(lesson_booking=pr_booking), self.student_helper.lesson_bookings_for_student(self.student_profile)))

    """
    Test cases
    """

    def test_format_to_currency_returns_appropriate_format(self):

        balance = 250
        self.assertEqual(self.transaction_helper.format_to_currency(balance), "250.00 GBP")

    def test_balance_at_returns_right_balance_at_a_given_time(self):

        # Check balance after first transfer
        self.assertEqual(self.transaction_helper.balance_at(self.transfers, self.transfers[1].date), Decimal(250))

        # Check balance after second transfer
        self.assertEqual(self.transaction_helper.balance_at(self.transfers, self.transfers[0].date), Decimal(500))

    def test_assign_balances_assigns_right_balance_to_right_transaction(self):

        transactions = self.transaction_helper.assign_balances(self.transfers + self.lesson_bookings)
        # Transaction of 250 GBP done before a booking
        self.assertEqual(transactions[1].balance, Decimal(250))

        # Transaction of 250 GBP done after a booking of 10 GBP
        self.assertEqual(transactions[0].balance, Decimal(490))

from datetime import datetime, timedelta, date 
from decimal import *

class TimeHelper:
    """
    Contains methods to mutate times
    """
    def add_minutes_to_time(self, time, minutes):
        """
        Adds a number of minutes to a time
        """
        date_1 = datetime(2020, 10, 10, time.hour, time.minute, 0)
        return (date_1 + timedelta(minutes=minutes)).time()

class TransactionModelHelper:
    """
    Contains functions that help with transactions
    """

    def assign_balances(self, transactions):
        """
        Assigns the balance to each transaction
        """
        for transaction in transactions:
            transaction.balance = self.balance_at(transactions, transaction.date)

        return transactions

    def format_to_currency(self, value):
        """
        Formats a number to GBP currency
        """
        # Source: https://bobbyhadz.com/blog/python-format-float-as-currency
        return f"{value:.2f} GBP"

    def balance_at(self, transactions, date):
        """
        Calculates balance from list of transactions to a given date
        """
        new_trans = transactions[:]
        new_trans.sort(key = lambda trans: trans.date, reverse=False)
        total = Decimal(0)
        for transaction in new_trans:
            if transaction.date <= date:
                total += transaction.fee
            else:
                break
        return total

class StudentProfileModelHelper:
    """
    Contains methods that assist in model retrieval on student profiles
    """
    def lesson_bookings_for_student(self, student_profile):
        """
        Returns the lesson bookings for a given student profiles
        """
        from lessons.models.lesson_models import LessonBooking
        return list(filter(lambda lesson_booking: lesson_booking.lesson_request.student_profile.id==student_profile.id, LessonBooking.objects.all()))

    def transfers_for_student(self, student_profile):
        """
        Returns the transfers for a given student profile
        """
        from lessons.models.transfer_models import Transfer
        return list(filter(lambda transfer: transfer.lesson_booking.lesson_request.student_profile == student_profile, Transfer.objects.all()))

class TeacherProfileModelHelper:
    """
    Contains methods that assist in model retrieval on teacher profiles
    """
    def lesson_bookings_for_teacher(self, teacher_profile):
        """
        Returns the lesson bookings for a given teacher profiles
        """
        from lessons.models.lesson_models import LessonBooking
        return list(filter(lambda lesson_booking: lesson_booking.teacher.id==teacher_profile.id, LessonBooking.objects.all()))

class SchoolTermModelHelper:
    """
    Contains methods that helper with school term related tasks
    """
    # The amount of days until the end of the term that is considered 'almost' next term
    ALMOST_NEXT_TERM_DAY_PERIOD = 14

    def _is_date_within(self, spec_date, start_date, end_date):
        """
        Returns whether a provided date falls within two intervals
        """
        return spec_date <= end_date and spec_date >= start_date

    def current_term(self):
        """
        Returns the current term or None
        """
        from lessons.models.term_models import SchoolTerm
        for term in SchoolTerm.objects.all():
            if self._is_date_within(datetime.now().date(), term.start_date, term.end_date):
                return term

        return None

    def next_term(self):
        """
        Returns the next term or None
        """
        from lessons.models.term_models import SchoolTerm
        if SchoolTerm.objects.all().count() == 0:
            return None

        sorted_terms = list(SchoolTerm.objects.all())
        sorted_terms.sort(key=lambda term: term.start_date, reverse=False)

        current_term = self.current_term()
        if current_term:
            index = sorted_terms.index(current_term)

            if index == len(sorted_terms) - 1:
                return None # No next term
            else:
                return sorted_terms[index + 1]

        for term in sorted_terms:
            if date.today() < term.start_date:
                return term # Return this term as it is first in list that is next

        return None

    def default_term_for_bookings(self):
        """
        Decides the best term to prompt user with by default
        """
        current_term = self.current_term()
        next_term = self.next_term()

        if current_term and next_term:
            # Almost next term
            if (current_term.end_date - datetime.now().date()).days <= SchoolTermModelHelper.ALMOST_NEXT_TERM_DAY_PERIOD:
                return next_term
            else:
                return current_term
        elif current_term is None and next_term:
            # In break before next term
            return next_term
        elif current_term and next_term is None:
            # In current term where there is no next term
            return current_term
        else:
            # No terms likely specified
            return None

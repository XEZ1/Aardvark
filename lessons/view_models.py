from .helpers import TransactionModelHelper

class TransactionViewModel:
    """
    Used to display transaction within templates
    Acts as an interface for transfers and invoices
    """
    def __init__(self, **kwargs):
        """
        Check to see if transaction is being created from transfer or invoices
        """
        if 'transfer' in kwargs:
            transfer = kwargs.get('transfer')

            self.date = transfer.date
            self.fee = transfer.balance
            self.reference = "Payment"
            self.student = transfer.lesson_booking.lesson_request.student_profile

        if 'lesson_booking' in kwargs:
            lesson_booking = kwargs.get('lesson_booking')

            self.date = lesson_booking.start_date_actual()
            self.fee = lesson_booking.calculate_total_price() * -1
            self.reference = lesson_booking.invoice_number()
            self.lesson_booking = lesson_booking
            self.student = lesson_booking.lesson_request.student_profile

    @property
    def formatted_fee(self):
        """
        Returns fee as formatted: e.g. 1.00 GBP
        """
        helper = TransactionModelHelper()
        return helper.format_to_currency(self.fee)

    @property
    def formatted_balance(self):
        """
        Returns balance as formatted: e.g. 1.00 GBP
        """
        helper = TransactionModelHelper()
        return helper.format_to_currency(self.balance)

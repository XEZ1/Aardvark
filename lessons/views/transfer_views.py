from django.shortcuts import render, redirect
from lessons.forms.lesson_forms import *
from lessons.forms.user_forms import *
from lessons.forms.transfer_forms import *
from django.db import transaction
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from lessons.models.user_models import User, UserType
from django.views.decorators.http import require_POST, require_GET
from lessons.decorators import *
from django.http import HttpResponse
from lessons.view_models import TransactionViewModel
from lessons.helpers import *

@login_required
@user_types_permitted(['ADMIN', 'DIRECTOR'])
def register_transfer(request):
    """
    Shows user the form to register a transfer
    """
    if (request.method == 'POST'):
        form = RegisterTransferForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,
                "The transfer has been successfully registered.")
            return redirect('register_transfer')
    else:
        form = RegisterTransferForm()

    return render(request, 'templates/transfer/register_transfer.html', {'form': form})

@login_required
@user_types_permitted(['STUDENT', 'ADMIN', 'DIRECTOR'])
def view_transactions(request, email):
    """
    Display transactions for a specified student profile
    """
    try:
        student_helper = StudentProfileModelHelper()
        transaction_helper = TransactionModelHelper()

        student_profile = User.objects.get(username=email).student_profile

        transfers = list(map(lambda pr_transfer: TransactionViewModel(transfer=pr_transfer), student_helper.transfers_for_student(student_profile)))
        lesson_bookings = list(map(lambda pr_booking: TransactionViewModel(lesson_booking=pr_booking), student_helper.lesson_bookings_for_student(student_profile)))

        transactions = transaction_helper.assign_balances(transfers + lesson_bookings)
        transactions.sort(key = lambda trans: trans.date, reverse=True)

        if len(transactions) > 0:
            last_transaction = transactions[0]
        else:
            last_transaction = None

        return render(request, 'templates/transfer/view_transactions.html',
            {
            'transactions': transactions,
            'student_profile': student_profile,
            'last_transaction': last_transaction,
            'view_all': False
            })

    except User.DoesNotExist:
        transactions = []
        messages.add_message(request, messages.ERROR,
                "The user you attempted to view the transactions for was not found.")
        return redirect('view_students')

@login_required
@user_types_permitted(['ADMIN', 'DIRECTOR'])
def view_all_transactions(request):
    """
    Display transactions for the entire school
    """
    transaction_helper = TransactionModelHelper()

    transfers = list(map(lambda pr_transfer: TransactionViewModel(transfer=pr_transfer), Transfer.objects.all()))
    lesson_bookings = list(map(lambda pr_booking: TransactionViewModel(lesson_booking=pr_booking), LessonBooking.objects.all()))
    combined_list = transfers + lesson_bookings

    transactions = transaction_helper.assign_balances(combined_list)
    transactions.sort(key = lambda trans: trans.date, reverse=True)

    if len(transactions) > 0:
        last_transaction = transactions[0]
    else:
        last_transaction = None

    return render(request, 'templates/transfer/view_transactions.html',
        {
        'transactions': transactions,
        'last_transaction': last_transaction,
        'view_all': True
        })

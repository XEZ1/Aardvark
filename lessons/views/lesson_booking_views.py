from django.shortcuts import render, redirect
from lessons.forms.lesson_forms import *
from lessons.forms.user_forms import *
from django.db import transaction
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from lessons.models.user_models import User, UserType
from django.views.decorators.http import require_POST, require_GET
from lessons.decorators import *
from django.http import HttpResponse
from lessons.helpers import SchoolTermModelHelper

"""
Generic (no specifc type) - Login required
The view below can only be accessed by authenticated users, although the type of user is not checked.
Docs on login_required: https://docs.djangoproject.com/en/4.1/topics/auth/default/#the-login-required-decorator
"""

@login_required
@user_types_permitted(['STUDENT', 'ADMIN', 'DIRECTOR'])
def view_invoice_for_lesson_booking(request, id):
    try:
        if request.user.type == UserType.STUDENT:
            lesson_bookings = list(filter(lambda lesson_booking: lesson_booking.lesson_request.student_profile.user == request.user, LessonBooking.objects.filter(id=id)))

            if (request.user.student_profile.is_parent()):
                for child in request.user.student_profile.children.all():
                    lesson_bookings.extend(list(filter(lambda lesson_booking: lesson_booking.lesson_request.student_profile == child, LessonBooking.objects.filter(pk=id))))
        else:
            lesson_bookings = LessonBooking.objects.filter(id=id)

        if len(lesson_bookings) > 0:
            lesson_booking = lesson_bookings[0]
        else:
            raise LessonBooking.DoesNotExist('Lesson booking does not exist')

        return render(request, 'templates/lesson/lesson_booking_invoice.html', {'lesson_booking': lesson_booking })
    except LessonBooking.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                "The lesson booking you tried to view the invoice for was not found.")
        return redirect('view_lesson_bookings')

@login_required
@user_types_permitted(['STUDENT'])
def request_repeat_booking(request, id):
    """
    Prompt user to request a repeat of lesson booking with id
    """
    try:
        lesson_bookings = list(filter(lambda lesson_booking: lesson_booking.lesson_request.student_profile.user == request.user, LessonBooking.objects.filter(id=id)))

        #children can only request a repeat of their own lessons
        #but parents can request repeats of their kid's lessons
        if (request.user.student_profile.is_parent()):
            for child in request.user.student_profile.children.all():
                lesson_bookings.extend(list(filter(lambda lesson_booking: lesson_booking.lesson_request.student_profile == child, LessonBooking.objects.filter(pk=id))))

        if len(lesson_bookings) > 0:
            lesson_booking = lesson_bookings[0]
        else:
            raise LessonBooking.DoesNotExist('Lesson booking does not exist')

        if (request.method == 'POST'):
            try:
                #create lesson
                form = RequestLessonForm(request.user, lesson_booking, request.POST)
                if form.is_valid():
                    form.save()
                    messages.add_message(request, messages.SUCCESS,
                        "The lesson booking has been successfully created.")
                    return redirect('view_lesson_requests')
            except:
                messages.add_message(request, messages.ERROR,
                    "Failed to request a repeat of the lesson booking.")
        else:
            form = RequestLessonForm(request.user, instance=lesson_booking.lesson_request, initial={
                'availability': lesson_booking.lesson_request.availability_formatted_as_list(),
                'recipient_profile_id': lesson_booking.lesson_request.student_profile.id
                })

            
            return render(request, 'templates/lesson/request_lesson.html', {'form': form, 'previous_booking': lesson_booking })
    except LessonBooking.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                "The lesson booking you attempted to request a repeat for was not found.")

    return redirect('view_lesson_bookings')

@login_required
@user_types_permitted(['ADMIN', 'DIRECTOR'])
def book_lesson(request, id):
    """
    Prompt user to book a lesson based off a student lesson request
    """
    try:
        lesson_requests = list(filter(lambda curr_lesson_request: curr_lesson_request.status() == "Unfulfilled" and curr_lesson_request.id == id,
            LessonRequest.objects.all()))

        if len(lesson_requests) > 0:
            lesson_request = lesson_requests[0]
        else:
            raise LessonRequest.DoesNotExist('Lesson request does not exist')

        if (request.method == 'POST'):
            form = BookLessonForm(request.user, lesson_request, request.POST)
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.SUCCESS,
                    "The lesson has been successfully booked.")
                return redirect('view_lesson_requests')
        else:
            helper = SchoolTermModelHelper()

            if lesson_request.previous_booking:
                messages.add_message(request, messages.INFO,
                    "The previous lesson booking's information has been automatically transfered to the below form, if you wish to update, you can change the values here.")
                form = BookLessonForm(request.user, lesson_request, instance=lesson_request.previous_booking, initial={'school_term': helper.default_term_for_bookings()})
            else:
                form = BookLessonForm(request.user, lesson_request, initial={'school_term': helper.default_term_for_bookings()})

        return render(request, 'templates/lesson/book_lesson.html', {'form': form, 'lesson_request': lesson_request})

    except LessonRequest.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                "The lesson request you attempted to book was either not found or has already been fulfilled.")

    return redirect('view_lesson_requests')

@login_required
def view_lesson_bookings(request):
    """
    Prompt user to view lesson bookings
    """
    if request.user.type == UserType.STUDENT:
        lesson_bookings = list(filter(lambda lesson_booking: lesson_booking.lesson_request.student_profile.user == request.user, LessonBooking.objects.all()))

        # Students don't get filtering options or get to view other student's bookings.
        if (request.user.student_profile.is_child()):
            # Children can only see their bookings
            return render(request, 'templates/lesson/view_lesson_bookings.html', {'lesson_bookings': lesson_bookings })
        else:
            # Parents can see not only their lesson requests, but also their childrens
            for child in request.user.student_profile.children.all():
                lesson_bookings.extend(list(filter(lambda lesson_booking: lesson_booking.lesson_request.student_profile == child, LessonBooking.objects.all())))

            # sort lesson bookings by date they start
            lesson_bookings.sort(key=lambda booking: booking.start_date_actual(), reverse=True)
            return render(request, 'templates/lesson/view_lesson_bookings.html', {'lesson_bookings':  lesson_bookings})
    elif request.user.type == UserType.ADMIN or request.user.type == UserType.DIRECTOR:
        # Users that possess an AdminProfile can view all lesson_bookings
        search_term = request.GET.get('search_term')

        if (search_term):
            search_term = search_term.lower().strip(' ')

            # Do query outside of django quering language as it uses derrived fields that cannot be operated on via SQL
            lesson_bookings = list(filter(lambda lesson_booking: search_term in lesson_booking.lesson_request.student_profile.user.full_name().lower() or search_term in lesson_booking.lesson_request.student_profile.user.email.lower(),
                LessonBooking.objects.all()))
        else:
            lesson_bookings = LessonBooking.objects.all()

        results_found = len(lesson_bookings)
        if results_found == 0 and search_term:
            # sort lesson bookings by date they start
            lesson_bookings.sort(key=lambda booking: booking.start_date_actual(), reverse=True)
            messages.add_message(request, messages.ERROR,
                    "No lesson bookings with students matching your search term were found.")
        elif search_term:
            messages.add_message(request, messages.INFO,
                    f"Found {results_found} lesson bookings that matched your search term.")

        return render(request, 'templates/lesson/view_lesson_bookings_extended.html', {'lesson_bookings': lesson_bookings, 'teacher': False})

    else:
        # Users that possess a Teacher profile can view their lesson_bookings
        search_term = request.GET.get('search_term')

        if (search_term):
            search_term = search_term.lower().strip(' ')

            # Do query outside of django quering language as it uses derrived fields that cannot be operated on via SQL
            lesson_bookings = list(filter(lambda lesson_booking: search_term in lesson_booking.lesson_request.student_profile.user.full_name().lower() or search_term in lesson_booking.lesson_request.student_profile.user.email.lower(),
                LessonBooking.objects.filter(teacher=request.user.teacher_profile)))
        else:
            lesson_bookings = LessonBooking.objects.filter(teacher=request.user.teacher_profile)

        results_found = len(lesson_bookings)
        if results_found == 0 and search_term:
            # sort lesson bookings by date they start
            lesson_bookings.sort(key=lambda booking: booking.start_date_actual(), reverse=True)
            messages.add_message(request, messages.ERROR,
                    "No lesson bookings within your timetable matching your search term were found.")
        elif search_term:
            messages.add_message(request, messages.INFO,
                    f"Found {results_found} lesson bookings that matched your search term in your timetable.")

        return render(request, 'templates/lesson/view_lesson_bookings_extended.html', {'lesson_bookings': lesson_bookings, 'teacher': True})

@login_required
@user_types_permitted(['ADMIN', 'DIRECTOR'])
def delete_lesson_booking(request, id):
    """
    Prompt user to delete the selected lesson booking
    """
    try:
        lesson_bookings = LessonBooking.objects.filter(id=id)

        if len(lesson_bookings) > 0:
            lesson_booking = lesson_bookings[0]
        else:
            raise LessonBooking.DoesNotExist('Lesson booking does not exist')

        if (request.method == 'POST'):
            try:
                lesson_booking.delete()
                messages.add_message(request, messages.SUCCESS,
                    "Lesson booking deleted successfully.")
            except:
                messages.add_message(request, messages.ERROR,
                    "Failed to delete the lesson booking.")
        else:
            return render(request, 'templates/lesson/delete_lesson_booking.html', {'lesson_booking': lesson_booking })
    except LessonBooking.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                "The lesson booking you attempted to delete was not found.")

    return redirect('view_lesson_bookings')

@login_required
@user_types_permitted(['ADMIN', 'DIRECTOR'])
def update_lesson_booking(request, id):
    """
    Prompt user to update lesson booking
    """
    try:
        lesson_bookings = LessonBooking.objects.filter(id=id)

        if len(lesson_bookings) > 0:
            lesson_booking = lesson_bookings[0]
        else:
            raise LessonBooking.DoesNotExist('Lesson booking does not exist')

        if (request.method == 'POST'):
            #try:
            form = UpdateLessonBookingForm(request.POST, instance=lesson_booking)
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.SUCCESS,
                    "The lesson booking has been successfully updated.")
                return redirect('view_lesson_bookings')
            else:
                return render(request, 'templates/lesson/update_lesson_booking.html',
                    {'lesson_booking': lesson_booking,
                    'form': form })
        else:
            form = UpdateLessonBookingForm(instance=lesson_booking)
            return render(request, 'templates/lesson/update_lesson_booking.html', {'lesson_booking': lesson_booking, 'form': form })
    except LessonBooking.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                "The lesson booking you attempted to update was not found.")
        return redirect('view_lesson_bookings')

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

"""
Generic (no specifc type) - Login required
The view below can only be accessed by authenticated users, although the type of user is not checked.
Docs on login_required: https://docs.djangoproject.com/en/4.1/topics/auth/default/#the-login-required-decorator
"""

@login_required
@user_types_permitted(['STUDENT'])
def request_lesson(request):
    """
    Prompt user to request a lesson
    """
    if (request.method == 'POST'):
        form = RequestLessonForm(request.user, None, request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,
                "The lesson request has been successfully created.")
            return redirect('view_lesson_requests')
    else:
        form = RequestLessonForm(request.user)

    return render(request, 'templates/lesson/request_lesson.html', {'form': form, 'repeat_booking_id': None })

@login_required
@user_types_permitted(['STUDENT', 'ADMIN', 'DIRECTOR'])
def view_lesson_requests(request):
    """
    Prompt user to view lesson requests
    """
    if request.user.type == UserType.STUDENT:
        # Students don't get filtering options or get to view other student's requests.
        if (request.user.student_profile.is_child()):
            lesson_requests = list(request.user.student_profile.lesson_requests.all())
            lesson_requests.sort(key=lambda request: request.status(), reverse=True)

            return render(request, 'templates/lesson/view_lesson_requests.html', {'lesson_requests': lesson_requests })
        else:
            # Parents can see not only their lesson requests, but also their childrens
            lesson_requests = list(request.user.student_profile.lesson_requests.all())
            for child in request.user.student_profile.children.all():
                lesson_requests.extend(list(child.lesson_requests.all()))

            lesson_requests.sort(key=lambda request: request.status(), reverse=True)
            return render(request, 'templates/lesson/view_lesson_requests.html', {'lesson_requests':  lesson_requests})
    else:
        # Users that possess an AdminProfile can view all lesson_requests
        search_term = request.GET.get('search_term')

        if (search_term):
            search_term = search_term.lower().strip(' ')

            # Do query outside of django quering language as it uses derrived fields that cannot be operated on via SQL
            lesson_requests = list(filter(lambda lesson_request: search_term in lesson_request.student_profile.user.full_name().lower() or search_term in lesson_request.student_profile.user.email.lower(),
                LessonRequest.objects.all()))
        else:
            lesson_requests = list(LessonRequest.objects.all())

        results_found = len(lesson_requests)
        lesson_requests.sort(key=lambda request: request.status(), reverse=True)
        if results_found == 0 and search_term:
            messages.add_message(request, messages.ERROR,
                    "No lesson requests with students matching your search term were found.")
        elif search_term:
            messages.add_message(request, messages.INFO,
                    f"Found {results_found} lesson requests that matched your search term.")

        return render(request, 'templates/lesson/view_lesson_requests_extended.html', {'lesson_requests': lesson_requests})

@login_required
@user_types_permitted(['STUDENT'])
def update_lesson_request(request, id):
    """
    Prompt user to update lesson request
    """
    try:
        lesson_requests = list(filter(lambda curr_lesson_request:
            curr_lesson_request.status() == "Unfulfilled" and
            (curr_lesson_request.student_profile == request.user.student_profile or curr_lesson_request.student_profile in request.user.student_profile.children.all()) and
            curr_lesson_request.id == id,
            LessonRequest.objects.all()))

        if len(lesson_requests) > 0:
            lesson_request = lesson_requests[0]
        else:
            raise LessonRequest.DoesNotExist('Lesson request does not exist')

        if (request.method == 'POST'):
            try:
                form = UpdateLessonRequestForm(request.POST, instance=lesson_request)
                if form.is_valid():
                    form.save()
                    messages.add_message(request, messages.SUCCESS,
                        "The lesson request has been successfully updated.")
                    return redirect('view_lesson_requests')
                else:
                    return render(request, 'templates/lesson/update_lesson_request.html',
                        {'lesson_request': lesson_request,
                        'form': form })
            except:
                messages.add_message(request, messages.ERROR,
                    "Failed to update the lesson request.")
                return redirect('view_lesson_requests')
        else:
            form = UpdateLessonRequestForm(instance=lesson_request, initial={'availability': lesson_request.availability_formatted_as_list()})
            return render(request, 'templates/lesson/update_lesson_request.html', {'lesson_request': lesson_request, 'form': form })
    except LessonRequest.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                "The lesson request you attempted to update was either not found or has already been fulfilled.")
        return redirect('view_lesson_requests')

@login_required
@user_types_permitted(['STUDENT'])
def delete_lesson_request(request, id):
    """
    Prompt user to delete the selected lesson request
    """
    try:
        lesson_requests = list(filter(lambda curr_lesson_request:
            curr_lesson_request.status() == "Unfulfilled" and
            (curr_lesson_request.student_profile == request.user.student_profile or curr_lesson_request.student_profile in request.user.student_profile.children.all()) and
            curr_lesson_request.id == id,
            LessonRequest.objects.all()))

        if len(lesson_requests) > 0:
            lesson_request = lesson_requests[0]
        else:
            raise LessonRequest.DoesNotExist('Lesson request does not exist')

        if (request.method == 'POST'):
            try:
                lesson_request.delete()
                messages.add_message(request, messages.SUCCESS,
                    "Lesson request deleted successfully.")
            except:
                messages.add_message(request, messages.ERROR,
                    "Failed to delete the lesson request.")
        else:
            return render(request, 'templates/lesson/delete_lesson_request.html', {'lesson_request': lesson_request })
    except LessonRequest.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                "The lesson request you attempted to delete was either not found or has already been fulfilled.")

    return redirect('view_lesson_requests')

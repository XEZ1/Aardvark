from django.shortcuts import render, redirect
from lessons.forms.lesson_forms import *
from lessons.forms.user_forms import *
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
def log_out(request):
    """
    Logs out the specified user
    """
    logout(request)
    return redirect('log_in')

@login_required
def dashboard(request):
    """
    Depending on type, points user to specific dashbaord relavent to their functionality.
    Cannot navigate to a dashboard if the user isn't logged in
    """

    # Getting current user: https://docs.djangoproject.com/en/4.1/topics/auth/default/#authentication-in-web-requests
    # Guarentted to not be annonymous as view is protected by @login_required
    user = request.user

    if (user.type == UserType.STUDENT):
        return render(request, 'templates/student/student_dashboard.html')
    elif (user.type == UserType.ADMIN):
        return render(request, 'templates/admin/admin_dashboard.html')
    elif(user.type == UserType.TEACHER):
        return render(request, 'templates/teacher/teacher_dashboard.html')
    else:
        return render(request, 'templates/director/director_dashboard.html')

"""
Guest required
The views below cannot be accessed by authenticated users.
Docs on user_passes_test: https://docs.djangoproject.com/en/4.1/topics/auth/default/#django.contrib.auth.decorators.user_passes_test
"""

@user_types_permitted(['GUEST'])
def log_in(request):
    """
    Prompt user to sign in to the system
    This can be used by any type, be it a student, teacher, or director
    """
    if request.method == 'POST':
        form = LoginUserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                # User successfully authenticated
                login(request, user)
                return redirect('dashboard')
            else:
                messages.add_message(request, messages.ERROR,
                    "Email and password combination do not match a valid user. Please try again.")

    form = LoginUserForm()
    return render(request, 'templates/log_in.html', {'form': form})

"""
Teacher
"""

@login_required
@user_types_permitted(['DIRECTOR'])
def register_teacher(request):
    """
    Prompts a director to register a teacher
    """
    if (request.method == 'POST'):
        form = RegisterTeacherForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.add_message(request, messages.SUCCESS,
                    "The teacher account has been successfully created.")
            return redirect('register_teacher')
    else:
        form = RegisterTeacherForm()

    return render(request, 'templates/teacher/register_teacher.html', {'form': form})

@login_required
@user_types_permitted(['DIRECTOR'])
def view_teachers(request):
    """
    Prompt user to view teacher accounts
    """
    return render(request, 'templates/teacher/view_teachers.html', {'teachers': User.objects.filter(type=UserType.TEACHER)})

@login_required
@user_types_permitted(['DIRECTOR'])
def delete_teacher(request, email):
    """
    Prompt user to delete teacher account
    """
    try:
        teacher_user = User.objects.filter(type=UserType.TEACHER).get(username=email)

        if (request.method == 'POST'):
            try:
                teacher_user.delete()
                messages.add_message(request, messages.SUCCESS,
                    "Teacher account deleted successfully.")
            except:
                messages.add_message(request, messages.ERROR,
                    "Failed to delete the teacher account.")
        else:
            return render(request, 'templates/teacher/delete_teacher.html', {'teacher': teacher_user })
    except User.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                "Teacher account you attempted to delete was not found.")

    return redirect('view_teachers')

@login_required
@user_types_permitted(['DIRECTOR'])
def update_teacher(request, email):
    """
    Prompt user to update teacher account
    """
    try:
        teacher = User.objects.filter(type=UserType.TEACHER).get(username=email)

        if (request.method == 'POST'):
            try:
                form = UpdateTeacherForm(request.POST, instance=teacher)
                if form.is_valid():
                    form.save()
                    messages.add_message(request, messages.SUCCESS,
                        "The teacher account has been successfully updated.")
                    return redirect('view_teachers')
                else:
                    return render(request, 'templates/teacher/update_teacher.html', {'teacher': teacher, 'form': form })
            except:
                messages.add_message(request, messages.ERROR,
                    "Failed to update the teacher account.")
                return redirect('view_teachers')
        else:
            form = UpdateTeacherForm(instance=teacher, initial={'email': teacher.email})
            return render(request, 'templates/teacher/update_teacher.html', {'teacher': teacher, 'form': form })
    except User.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                "Teacher account you attempted to update was not found.")
        return redirect('view_teachers')

"""
Admins + general
"""

"""
Multiple db operations take place, this ensures damage-control in event of failure.
Only guests or admins can access this view. That is, to either register as a student, or register a new admin
Docs: https://docs.djangoproject.com/en/4.1/topics/db/transactions/
"""
@transaction.non_atomic_requests
@user_types_permitted(['GUEST', 'STUDENT_PARENT', 'DIRECTOR', 'STUDENT_UNASSOC'])
def register(request):
    """
    Prompt user to register themselves as a student.
    """
    # Docs: https://docs.djangoproject.com/en/4.1/ref/contrib/auth/#django.contrib.auth.models.User.is_anonymous
    if (request.user.is_anonymous):
        if (request.method == 'POST'):
            # Parent variable had to be specifed as 'None' so that request.POST parameter is passed correctly.
            form = RegisterStudentForm(None, request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                return redirect('dashboard')
        else:
            form = RegisterStudentForm()

        return render(request, 'templates/student/register_student.html', {'form': form})
    elif (request.user.type == UserType.DIRECTOR): # Will be a director due to elimination and protection on view
        if (request.method == 'POST'):
            form = RegisterAdminForm(request.POST)
            if form.is_valid():
                user = form.save()
                messages.add_message(request, messages.SUCCESS,
                    "The administrator account has been successfully created.")
                return redirect('register')
        else:
            form = RegisterAdminForm()

        return render(request, 'templates/admin/register_admin.html', {'form': form})
    else: # Must be a student by filtering and decorator protection
        if (request.method == 'POST'):
            # Pass in parent
            form = RegisterStudentForm(request.user.student_profile, request.POST)
            if form.is_valid():
                user = form.save()
                messages.add_message(request, messages.SUCCESS,
                    "Your child has been successfully registered.")
                return redirect('register')
        else:
            form = RegisterStudentForm()

        return render(request, 'templates/student/register_student_child.html', {'form': form})

@login_required
@user_types_permitted(['STUDENT_PARENT'])
def view_children(request):
    return render(request, 'templates/student/view_children.html', {'children': request.user.student_profile.children.all()} )

@login_required
@user_types_permitted(['DIRECTOR'])
def view_admins(request):
    """
    Prompt user to view admin accounts
    """
    return render(request, 'templates/admin/view_admins.html', {'admins': User.objects.filter(type=UserType.ADMIN)})

@login_required
@user_types_permitted(['ADMIN', 'DIRECTOR'])
def view_students(request):
    """
    Prompt user to view student accounts
    """
    search_term = request.GET.get('search_term')

    if (search_term):
        search_term = search_term.lower().strip(' ')

        students = list(filter(lambda student: search_term in student.user.full_name().lower() or search_term in student.user.email.lower(),
            StudentProfile.objects.all()))
    else:
        students = StudentProfile.objects.all()

    results_found = len(students)
    if results_found == 0 and search_term:
        messages.add_message(request, messages.ERROR,
                "No students matching your search term were found.")
    elif search_term:
        messages.add_message(request, messages.INFO,
                f"Found {results_found} students that matched your search term.")

    return render(request, 'templates/student/view_students.html', {'students': students})

@login_required
@user_types_permitted(['DIRECTOR'])
def delete_admin(request, email):
    """
    Prompt user to delete admin account
    """
    try:
        admin_user = User.objects.filter(type=UserType.ADMIN).get(username=email)

        if (request.method == 'POST'):
            try:
                admin_user.delete()
                messages.add_message(request, messages.SUCCESS,
                    "Administrator account deleted successfully.")
            except:
                messages.add_message(request, messages.ERROR,
                    "Failed to delete the administrator account.")
        else:
            return render(request, 'templates/admin/delete_admin.html', {'admin': admin_user })
    except User.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                "Administrator account you attempted to delete was not found.")

    return redirect('view_admins')

@login_required
@user_types_permitted(['DIRECTOR'])
def update_admin(request, email):
    """
    Prompt user to update admin account
    """
    try:
        admin = User.objects.filter(type=UserType.ADMIN).get(username=email)

        if (request.method == 'POST'):
            try:
                form = UpdateAdminForm(request.POST, instance=admin)
                if form.is_valid():
                    form.save()
                    messages.add_message(request, messages.SUCCESS,
                        "The administrator account has been successfully updated.")
                    return redirect('view_admins')
                else:
                    return render(request, 'templates/admin/update_admin.html', {'admin': admin, 'form': form })
            except:
                messages.add_message(request, messages.ERROR,
                    "Failed to update the administrator account.")
                return redirect('view_admins')
        else:
            form = UpdateAdminForm(instance=admin, initial={'email': admin.email})
            return render(request, 'templates/admin/update_admin.html', {'admin': admin, 'form': form })
    except User.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                "Administrator account you attempted to update was not found.")
        return redirect('view_admins')

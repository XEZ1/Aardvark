from django.shortcuts import render, redirect
from lessons.forms.term_forms import RegisterSchoolTermForm
from django.contrib import messages
from lessons.decorators import user_types_permitted
from django.contrib.auth.decorators import login_required
from lessons.models.term_models import *
from lessons.forms.term_forms import *

@login_required
@user_types_permitted(['ADMIN', 'DIRECTOR'])
def register_school_term(request):
    if (request.method == 'POST'):
        form = RegisterSchoolTermForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,
                "The school term was successfully registered.")

            return redirect('register_school_term')
    else:
        form = RegisterSchoolTermForm()

    return render(request, 'templates/term/register_school_term.html', { "form": form })

@login_required
@user_types_permitted(['ADMIN', 'DIRECTOR'])
def update_school_term(request, id):
    """
    Prompt user to update term
    """
    try:
        term = SchoolTerm.objects.get(id=id)

        if (request.method == 'POST'):
            try:
                form = UpdateSchoolTermForm(request.POST, instance=term)
                if form.is_valid():
                    form.save()
                    messages.add_message(request, messages.SUCCESS,
                        "The school term has been successfully updated.")
                    return redirect('view_school_terms')
                else:
                    return render(request, 'templates/term/update_school_term.html', {'term': term, 'form': form })
            except:
                messages.add_message(request, messages.ERROR,
                    "Failed to update the school term.")
                return redirect('view_school_terms')
        else:
            form = UpdateSchoolTermForm(instance=term)
            return render(request, 'templates/term/update_school_term.html', {'term': term, 'form': form })
    except SchoolTerm.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                "The school term you attempted to update was not found.")
        return redirect('view_school_terms')

@login_required
@user_types_permitted(['ADMIN', 'DIRECTOR', 'TEACHER'])
def view_school_terms(request):
    """
    show user all of the school terms
    """
    if request.user.type == UserType.TEACHER:
        return render(request, 'templates/term/view_school_terms.html', {'terms': SchoolTerm.objects.all(), 'readonly': True})
    else:
        return render(request, 'templates/term/view_school_terms.html', {'terms': SchoolTerm.objects.all(), 'readonly': False})

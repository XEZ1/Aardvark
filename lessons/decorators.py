from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from msms.settings import DASHBOARD_URL
from lessons.models.user_models import User, UserType

"""
This file contains custom decorators used to restrict access to certain views base on conditions
Docs of this: https://docs.djangoproject.com/en/2.2/_modules/django/contrib/admin/views/decorators/
"""

def user_types_permitted(user_types, view_func=None, redirect_field_name=None, login_url=DASHBOARD_URL):
    """
    Checks for a specific type of user
    GUEST = Not yet logged on
    STUDENT = Any student type
    STUDENT_UNASSOC = Any student that is both not a parent and not a child
    STUDENT_PARENT = A student which has registered at least one child
    STUDENT_CHILD = A student which has a parent
    ADMIN = A system administrator
    DIRECTOR = A system director
    TEACHER = A teacher in the school
    """
    def _matches_user_types(user):
        """
        Checks based on user type conditions
        """
        if user.is_authenticated:
            if 'STUDENT_UNASSOC' in user_types and user.type == UserType.STUDENT and user.student_profile.is_parent() == False and user.student_profile.is_child() == False:
                return True
            elif 'STUDENT_PARENT' in user_types and user.type == UserType.STUDENT and user.student_profile.is_parent():
                return True
            elif 'STUDENT_CHILD' in user_types and user.type == UserType.STUDENT and user.student_profile.is_child():
                return True
            elif 'ADMIN' in user_types and user.type == UserType.ADMIN:
                return True
            elif 'DIRECTOR' in user_types and user.type == UserType.DIRECTOR:
                return True
            elif 'STUDENT' in user_types and user.type == UserType.STUDENT:
                return True
            elif 'TEACHER' in user_types and user.type == UserType.TEACHER:
                return True
        else:
            if 'GUEST' in user_types:
                return True

        return False

    custom_decorator = user_passes_test(_matches_user_types, login_url=login_url, redirect_field_name=redirect_field_name)
    return custom_decorator(view_func) if view_func else custom_decorator

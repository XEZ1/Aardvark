from django import forms
from lessons.models import User, UserType, StudentProfile, AdminProfile, TeacherProfile
from django.core.validators import RegexValidator

class LoginUserForm(forms.Form):
    """
    The form that is user to log a user in
    """
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class UpdateTeacherForm(forms.ModelForm):
    """
    The form used to edit an underlying model
    """

    class Meta():
        """
        Select model fields that will be used within form.
        """
        model = User
        fields = [ 'first_name', 'last_name' ]

    email = forms.EmailField(required=True)
    password = forms.CharField(
        label='New password (leave blank to remain unchanged)',
        required=False,
        widget=forms.PasswordInput(),
        validators=[
            RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message="Password must contain upper, lower case letter and number"
        )])

    password_confirm = forms.CharField(label='Confirm new password', widget=forms.PasswordInput(), required=False)

    def clean(self):
        """
        Docs on this https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#overriding-the-clean-method
        """
        super().clean()

        prospective_email = self.cleaned_data.get('email')
        if prospective_email.lower().strip(' ') != self.instance.email:
            # User has changed the email of the user beyond capitalisation and trailing spaces
            if User.objects.filter(username=prospective_email).count() > 0:
                self.add_error('email', 'Email is already taken by another user')

        # If the fields password and password_confirm don't match, an error is added.
        if self.cleaned_data.get('password') != self.cleaned_data.get('password_confirm'):
            self.add_error('password_confirm', 'Password confirmation not equal to password')

    def save(self):
        """
        Updates the user model
        """
        super().save(commit=False)

        user = self.instance

        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.username = self.cleaned_data.get('email')
        
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data.get('password'))

        user.save()

        return user

class UpdateAdminForm(forms.ModelForm):
    """
    The form used to edit an underlying model
    """

    class Meta():
        """
        Select model fields that will be used within form.
        """
        model = User
        fields = [ 'first_name', 'last_name' ]

    email = forms.EmailField(required=True)
    password = forms.CharField(
        label='New password (leave blank to remain unchanged)',
        required=False,
        widget=forms.PasswordInput(),
        validators=[
            RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message="Password must contain upper, lower case letter and number"
        )])

    password_confirm = forms.CharField(label='Confirm new password', widget=forms.PasswordInput(), required=False)
    make_director = forms.BooleanField(label='Elevate account to director privileges?', required=False)

    def clean(self):
        """
        Docs on this https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#overriding-the-clean-method
        """
        super().clean()

        prospective_email = self.cleaned_data.get('email')
        if prospective_email.lower().strip(' ') != self.instance.email:
            # User has changed the email of the user beyond capitalisation and trailing spaces
            if User.objects.filter(username=prospective_email).count() > 0:
                self.add_error('email', 'Email is already taken by another user')

        # If the fields password and password_confirm don't match, an error is added.
        if self.cleaned_data.get('password') != self.cleaned_data.get('password_confirm'):
            self.add_error('password_confirm', 'Password confirmation not equal to password')

    def save(self):
        """
        Updates the user model
        """
        super().save(commit=False)

        user = self.instance

        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.username = self.cleaned_data.get('email')

        if (self.cleaned_data.get('make_director') == True):
            user.type = UserType.DIRECTOR

        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data.get('password'))

        user.save()

        return user

class RegisterUserForm(forms.ModelForm):
    """
    The base form for registering users.
    Every form, regardless of account type, has these fields.
    """
    class Meta():
        """
        Select model fields that will be used within form.
        """
        model = User
        fields = [ 'first_name', 'last_name', 'email']

    # Additional fields outside of model
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[
            RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message="Password must contain upper, lower case letter and number"
        )])

    password_confirm = forms.CharField(label='Confirm password', widget=forms.PasswordInput())

    def clean(self):
        """
        Used to check for validation errors that may occur ACROSS multiple fields
        """
        super().clean()

        # If the fields password and password_confirm don't match, an error is added.
        if self.cleaned_data.get('password') != self.cleaned_data.get('password_confirm'):
            self.add_error('password_confirm', 'Password confirmation not equal to password')

class RegisterStudentForm(RegisterUserForm):
    """
    The registration form for when guests want to make new student accounts
    """
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent

    def save(self):
        """
        Creates and saves a new student user with an associated empty student profile
        """
        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('email'),
            first_name = self.cleaned_data.get('first_name'),
            last_name = self.cleaned_data.get('last_name'),
            email = self.cleaned_data.get('email'),
            password = self.cleaned_data.get('password'),
            type = UserType.STUDENT,
            is_active=True)

        # Add empty student profile
        student_profile = StudentProfile()
        student_profile.user = user
        if (self.parent):
            student_profile.parent = self.parent
        student_profile.save()

        return user

class RegisterAdminForm(RegisterUserForm):
    """
    The registration form for when directors want to make new admin accounts
    """
    def save(self):
        """
        Creates and saves a new user with an associated empty admin profile
        """
        super().save(commit=False)

        user = User.objects.create_user(
            self.cleaned_data.get('email'),
            first_name = self.cleaned_data.get('first_name'),
            last_name = self.cleaned_data.get('last_name'),
            email = self.cleaned_data.get('email'),
            password = self.cleaned_data.get('password'),
            type = UserType.ADMIN,
            is_active=True)

        # Add empty admin profile
        admin_profile = AdminProfile()
        admin_profile.user = user
        admin_profile.save()

        return user
    
class RegisterTeacherForm(RegisterUserForm):
    """
    The registration form for when directors want to make new teacher accounts
    """
    def save(self):
        """
        Creates and saves a new user with an associated empty teacher profile
        """
        super().save(commit=False)

        user = User.objects.create_user(
            self.cleaned_data.get('email'),
            first_name = self.cleaned_data.get('first_name'),
            last_name = self.cleaned_data.get('last_name'),
            email = self.cleaned_data.get('email'),
            password = self.cleaned_data.get('password'),
            type = UserType.TEACHER,
            is_active=True)

        # Add empty admin profile
        teacher_profile = TeacherProfile()
        teacher_profile.user = user
        teacher_profile.save()

        return user

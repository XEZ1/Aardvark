from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models.user_models import User, UserType
from ..helpers import LoginHelper

class UserModelTestCase(TestCase, LoginHelper):
    """
    Contains the test cases for the user model that is used for authentication
    """
    def setUp(self):
        """
        Create a user that can be modified for the purposes of different test cases
        """
        self.user = User.objects.create_user(
            'janedoe@example.com',
            first_name='Jane',
            last_name='Doe',
            email='janedoe@example.com',
            password='Password123',
            type=UserType.STUDENT,
        )

    """
    Helper functions
    """

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail('Test setup user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def _create_second_user(self):
        user = User.objects.create_user(
            'johndoe@example.com',
            first_name='John',
            last_name='Doe',
            email='johndoe@example.com',
            password='Password123',
            type=UserType.STUDENT,
        )


        return user

    """
    Test cases
    """

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_full_name_must_be_correct(self):
        self.assertEqual(self.user.full_name(), "Jane Doe")

    def test_username_cannot_be_blank(self):
        self.user.username = ''
        self._assert_user_is_invalid()

    def test_username_must_equal_email(self):
        self.user.email = 'adifferent@gmail.com'
        self._assert_user_is_invalid()

    def test_username_must_be_unique(self):
        second_user = self._create_second_user()

        self.user.username = second_user.username

        # Ensures that the username = password check doesn't interfere
        self.user.email = second_user.email
        self._assert_user_is_invalid()

    def test_student_profile_full_name(self):
        self._create_student_user()
        self.assertEqual(self.student_user.student_profile.__str__(), "Jane Doe")

    def test_first_name_need_not_be_unique(self):
        second_user = self._create_second_user()

        self.user.first_name = second_user.first_name
        self._assert_user_is_valid()

    def test_first_name_cannot_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_first_name_can_be_50_chars(self):
        self.user.first_name = 'A' * 50
        self._assert_user_is_valid()

    def test_first_name_cannot_be_51_chars(self):
        self.user.first_name = 'A' * 51
        self._assert_user_is_invalid()

    def test_last_name_need_not_be_unique(self):
        second_user = self._create_second_user()

        self.user.last_name = second_user.last_name
        self._assert_user_is_valid()

    def test_last_name_cannot_be_blank(self):
        self.user.last_name = ''
        self._assert_user_is_invalid()

    def test_last_name_can_be_50_chars(self):
        self.user.last_name = 'A' * 50
        self._assert_user_is_valid()

    def test_last_name_cannot_be_51_chars(self):
        self.user.last_name = 'A' * 51
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        second_user = self._create_second_user()

        self.user.email = second_user.email
        self._assert_user_is_invalid()

    def test_email_cannot_be_blank(self):
        self.user.email = ''
        self._assert_user_is_invalid()

    def test_email_must_contain_username(self):
        self.user.email = '@example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_at_symbol(self):
        self.user.email = 'johndoe.example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_name(self):
        self.user.email = 'johndoe@.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_extension(self):
        self.user.email = 'johndoe@cheese.'
        self._assert_user_is_invalid()

    def test_email_must_not_contain_more_than_one_at(self):
        self.user.email = 'johndoe@@chese.org'
        self._assert_user_is_invalid()

    def test_type_must_be_set(self):
        self.user.type = None
        self._assert_user_is_invalid()
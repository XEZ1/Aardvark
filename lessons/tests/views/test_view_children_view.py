from django.test import TestCase
from lessons.models.user_models import UserType
from lessons.forms.user_forms import *
from django.urls import reverse
from ..helpers import LoginHelper, LessonHelper
from lessons.models.term_models import *

class ViewSeeChildren(TestCase, LoginHelper, LessonHelper):
    """
    Contains the test cases for the view see children
    """

    def setUp(self):
        """
        Get routed URL
        """

        self.url = reverse('view_children')


    """
    Test cases
    """

    def test_url(self):
        self.assertEqual(self.url, '/children/')

    def test_view_restricted_for_guest(self):
        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_login(response)

    def test_view_restricted_for_student_with_no_children(self):
        self._create_student_user()
        self._log_in_as_student()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response, UserType.STUDENT)

    def test_get_the_page_for_student_parent(self):
        self._create_student_user()
        self._create_child_user_for_student_user()
        self._log_in_as_student()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url)

        # Check for success HTTP response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'templates/student/view_children.html')

    def test_view_restricted_for_student_child(self):
        self._create_student_user()
        self._create_child_user_for_student_user()
        self._log_in_as_student_child()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)
        self.assert_redirected_to_dashboard(response, UserType.STUDENT)

    def test_how_many_children_shown(self):
        self._create_student_user()
        self._create_child_user_for_student_user()
        self._log_in_as_student()
        self.assertTrue(self._is_logged_in())

        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

        # Should only be a single displayed lesson request - their own
        children = response.context['children']
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].user.id, self.student_user_child.id)

        self.assertTemplateUsed(response, 'templates/student/view_children.html')

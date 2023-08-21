from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models.term_models import SchoolTerm
from datetime import datetime, timedelta
from lessons.tests.helpers import SchoolTermHelper, LoginHelper

class SchoolTermModelTestCase(TestCase, SchoolTermHelper, LoginHelper):

    def setUp(self):
        self._create_school_term()

    #copied from archie's helper functions in other test cases
    def _assert_model_is_valid(self):
        try:
            self.school_term.full_clean()
        except (ValidationError):
            self.fail('Test setup model should be valid')

    def _assert_model_is_invalid(self, school_term):
        with self.assertRaises(ValidationError):
            school_term.full_clean()

    def test_label_cannot_be_blank(self):
        # Term label must not be blank
        self.school_term.label = ''
        self._assert_model_is_invalid(self.school_term)

    def test_label_has_to_be_unique(self):
        # Make second school term with different props bar label
        school_term = SchoolTerm()
        school_term.label= "Term 1"
        school_term.start_date = datetime.now()+ timedelta(days=91)
        school_term.end_date = datetime.now()+ timedelta(days=191)

        self._assert_model_is_invalid(school_term)

    def test_label_cannot_be_51_chars(self):
        # Ensure term label is of reasonable length
        self.school_term.label = 'A' * 51
        self._assert_model_is_invalid(self.school_term)

    def test_overlap_on_dates_that_do_not_overlap(self):
        """
        Two selected dates should not overlap
        """
         # Term 1 dates
        date_start_1 = '2022-09-20'
        date_end_1 = '2022-09-29'

         # Term 1 dates
        date_start_2 = '2022-10-20'
        date_end_2 = '2022-10-29'

        self.assertEqual(self.school_term.overlaps(date_start_1, date_end_1, date_start_2, date_end_2), False)

    def test_overlap_on_dates_that_do_overlap(self):
        """
        Two selected dates should overlap
        """
        # Term 1 dates
        date_start_1 = '2022-09-20'
        date_end_1 = '2022-09-29'

        # Term 2 dates
        date_start_2 = '2022-09-20'
        date_end_2 = '2022-10-29'

        self.assertEqual(self.school_term.overlaps(date_start_1, date_end_1, date_start_2, date_end_2), True)
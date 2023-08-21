from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models.user_models import User, UserType
from lessons.models.lesson_models import *
from lessons.models.lesson_models import LessonRequest, AvailabilityPeriod
from lessons.models.term_models import SchoolTerm
from lessons.tests.helpers import LoginHelper, LessonHelper, SchoolTermHelper
from lessons.helpers import SchoolTermModelHelper
from datetime import datetime, timedelta

class SchoolTermModelHelperTestCase(TestCase, LoginHelper, LessonHelper, SchoolTermHelper, SchoolTermModelHelper):
    """
    Contains tests for the school term helper
    """
    def test_current_term_for_none(self):
        '''
        This test checks whether the current term return None if no terms have been created
        '''
        test = self.current_term() 
        self.assertEqual(test, None)

    def test_current_term(self):
        '''
        This test checks whether the current term returned is equal to the current term created
        '''
        test_case_term=self._create_school_term()

        curr_term = self.current_term()
        self.assertEqual(curr_term, test_case_term)

    def test_next_term_return_none_when_one_term_present(self):
        '''
        This test checks whether the next term return None if there is no terms
        '''
        test_case_term=self._create_school_term()
        self.assertEqual(self.next_term(), None)

    def test_next_term_return_none_when_no_term_present(self):
        '''
        This test checks whether the next term return None if there is only 1 term
        '''
        self.assertEqual(SchoolTerm.objects.count(), 0)
        self.assertEqual(self.next_term(), None)

    def test_next_term_return_next_term(self):
        '''
        This test checks whether the correct next term is equal to the next_term function
        '''
        test_case_term=self._create_school_term()

        #create secondary school term
        school_term = SchoolTerm()
        school_term.label = "Term 2"
        school_term.start_date = self.school_term.end_date + timedelta(days=1)
        school_term.end_date = school_term.start_date + timedelta(weeks=16)
        school_term.save()

        self.assertEqual(self.next_term(), school_term)
    
    def test_default_term_none_for_no_terms(self):
        '''
        This test checks whether the the default term is None when there are no terms
        '''
        self.assertEqual(self.default_term_for_bookings(), None)
    
    def test_default_term_for_bookings_correct(self):
        '''
        This test checks whether the default terms is equal is the current term which is correct
        '''
        #not near ending so should be default
        test_case_term=self._create_school_term()

        self.assertEqual(test_case_term, self.default_term_for_bookings())
    

    




        


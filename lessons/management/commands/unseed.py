from django.core.management.base import BaseCommand, CommandError
from lessons.models import *

class Command(BaseCommand):
    """
    Remove all seeded entities from database
    """
    def handle(self, *args, **options):
        """
        Delete all users that aren't staff or super user
        Foreign key constraints will causing profiles to be subsequently deleted
        """
        User.objects.filter(is_staff=False, is_superuser=False).delete()
        SchoolTerm.objects.all().delete()
        print("The process of unseeding the database has completed successfully")

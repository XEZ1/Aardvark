from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, MaxLengthValidator

class Transfer(models.Model):
    """
    Represents a bank transfer made
    """

    id = models.AutoField(primary_key=True)
    date = models.DateField(blank=False)
    balance = models.DecimalField(max_digits=6, decimal_places=2, blank=False, validators=[MinValueValidator(0.01)])

    # What is the transfer for?
    lesson_booking = models.ForeignKey('lessons.LessonBooking', on_delete=models.CASCADE, related_name="transfers", blank=False)

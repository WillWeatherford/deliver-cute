"""Subscriber model tracking preferences for each email."""
from django.db import models

HOUR_CHOICES = [(n, str(n) + ':00') for n in range(24)]


class Subscriber(models.Model):
    """Subscriber model tracking preferences for each email."""

    email = models.EmailField()
    send_hour = models.IntegerField(choices=HOUR_CHOICES, default=8)

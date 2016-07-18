"""Subscriber model tracking preferences for each email."""
from django.db import models


def get_hour(n):
    """Convert from 24-hour number range to 12-hour AM/PM format."""
    hour_num = n % 12 or 12
    ampm = 'AM' if n < 12 else 'PM'
    return (n, '{}:00 {}'.format(hour_num, ampm))

HOUR_CHOICES = map(get_hour, range(24))


class Subscriber(models.Model):
    """Subscriber model tracking preferences for each email."""

    email = models.EmailField()
    send_hour = models.IntegerField(choices=HOUR_CHOICES, default=8)

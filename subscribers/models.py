"""Subscriber model tracking preferences for each email."""
from django.db import models
from itertools import product

HOUR_CHOICES = [(num, '{}:00 {}'.format(num, am_pm))
                for am_pm, num in product(
                    ('AM', 'PM'),
                    [12] + list(range(1, 12)))
                ]


class Subscriber(models.Model):
    """Subscriber model tracking preferences for each email."""

    email = models.EmailField(unique=True)
    send_hour = models.IntegerField(choices=HOUR_CHOICES, default=8)

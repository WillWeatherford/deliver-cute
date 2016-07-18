from django.test import TestCase
from .models import Subscriber

DUMMY_EMAIL = 'example@example.com'


class SimpleCase(TestCase):
    """Very simple case to test instantiation of Subscriber class."""

    def test_initialize(self):
        """Test initialization of new Subscriber."""
        newsub = Subscriber(email=DUMMY_EMAIL)
        newsub.save()

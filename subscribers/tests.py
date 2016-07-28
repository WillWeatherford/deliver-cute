"""Testing Subscriber and SubReddit models."""

from django.test import TestCase
from .models import Subscriber, SubReddit
import factory

DUMMY_EMAIL = 'example@example.com'


class SubRedditFactory(factory.django.DjangoModelFactory):
    """Creates SubReddit models for testing."""

    class Meta:
        """Assign SubReddit model as product of factory."""

        model = SubReddit

    email = factory.Faker('email')


class SubscriberFactory(factory.django.DjangoModelFactory):
    """Creates Subscriber models for testing."""

    class Meta:
        """Assign Subscriber model as product of factory."""

        model = Subscriber

    email = factory.Faker('email')
    


class SimpleCase(TestCase):
    """Very simple case to test instantiation of Subscriber class."""

    def test_initialize(self):
        """Test initialization of new Subscriber."""
        newsub = Subscriber(email=DUMMY_EMAIL)
        newsub.save()

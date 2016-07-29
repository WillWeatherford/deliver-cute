"""Testing Subscriber and SubReddit models."""

from django.test import TestCase
from .models import Subscriber, SubReddit
import factory
from constants import SUBREDDIT_NAMES
import random

DUMMY_EMAIL = 'example@example.com'

# Test that both models load and save
# Test that subreddits can be associated to subs


class SubRedditFactory(factory.django.DjangoModelFactory):
    """Creates SubReddit models for testing."""

    class Meta:
        """Assign SubReddit model as product of factory."""

        model = SubReddit

    # use factory functionality to produce all instead of random ones.
    display_name = factory.Iterator(SUBREDDIT_NAMES)


class SubscriberFactory(factory.django.DjangoModelFactory):
    """Creates Subscriber models for testing."""

    class Meta:
        """Assign Subscriber model as product of factory."""

        model = Subscriber

    email = factory.Faker('email')
    send_hour = random.randrange(24)


class SimpleCase(TestCase):
    """Very simple case to test instantiation of Subscriber class."""

    def setUp(self):
        """Set up model instances."""
        self.subscriber = SubscriberFactory.create()
        self.subreddit = SubRedditFactory.create()

    def test_subscriber(self):
        """Test initialization of new Subscriber."""
        self.assertTrue(self.subscriber.pk)

    def test_subreddit(self):
        """Test initialization of new Subreddit."""
        self.assertTrue(self.subreddit.pk)

    def test_one_subscriber(self):
        """Test that one subscriber has been registered in the ORM."""
        self.assertEqual(Subscriber.objects.count(), 1)

    def test_one_subreddit(self):
        """Test that one subreddit has been registered in the ORM."""
        self.assertEqual(SubReddit.objects.count(), 1)

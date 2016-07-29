"""Testing Subscriber and SubReddit models."""

from constants import SUBREDDIT_NAMES
from django.test import TestCase
from .models import Subscriber, SubReddit
from factory.django import DjangoModelFactory
import factory
import random


class SubRedditFactory(DjangoModelFactory):
    """Creates SubReddit models for testing."""

    class Meta:
        """Assign SubReddit model as product of factory."""

        model = SubReddit

    display_name = factory.Iterator(SUBREDDIT_NAMES)


class SubscriberFactory(DjangoModelFactory):
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


class MultiCase(TestCase):
    """Multiple Subscribers with multiple subreddits."""

    def setUp(self):
        """Setup many Subscribers and SubReddits."""
        self.subreddits = SubRedditFactory.create_batch(len(SUBREDDIT_NAMES))
        self.subscribers = SubscriberFactory.create_batch(20)
        for s in self.subscribers:
            num = random.randrange(len(SUBREDDIT_NAMES))
            subscription = SubReddit.objects.order_by('?')[:num]
            s.subreddits.add(*subscription)

    def test_multiple(self):
        """Check that relationship is sound."""
        for s in self.subscribers:
            for sr in s.subreddits.all():
                self.assertTrue(sr.pk)

    def test_subscriber_str(self):
        """Check str method of Subscriber."""
        for s in self.subscribers:
            self.assertIsInstance(str(s), str)

    def test_subreddit_str(self):
        """Check str method of SubReddit."""
        for sr in self.subreddits:
            self.assertIn(str(sr), SUBREDDIT_NAMES)

    def test_subreddit_names(self):
        """Test subreddit_names method of Subscriber."""
        for s in self.subscribers:
            for name in s.subreddit_names():
                self.assertIn(name, SUBREDDIT_NAMES)

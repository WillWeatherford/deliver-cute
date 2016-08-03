"""Testing Subscriber and SubReddit models."""
from __future__ import unicode_literals, absolute_import

from django.test import TestCase
from nose_parameterized import parameterized

from subscribers.models import Subscriber, SubReddit
from constants import SUBREDDIT_NAMES
from tests.classes import (
    SubRedditFactory,
    SubscriberFactory,
    BATCH_PARAMS,
    SUBR_PARAMS,
)


class SimpleCase(TestCase):
    """Very simple case to test instantiation of Subscriber class."""

    def setUp(self):
        """Set up model instances."""
        self.subscriber = SubscriberFactory.create()
        self.subreddit = SubRedditFactory.create()

    @parameterized.expand(BATCH_PARAMS)
    def test_subscriber(self, idx):
        """Test initialization of new Subscriber."""
        self.assertTrue(self.subscriber.pk)

    @parameterized.expand(BATCH_PARAMS)
    def test_subreddit(self, idx):
        """Test initialization of new Subreddit."""
        self.assertTrue(self.subreddit.pk)

    @parameterized.expand(BATCH_PARAMS)
    def test_subscriber_unsub_hash(self, idx):
        """Test initialization of new Subreddit with an unsubscribe hash."""
        self.assertTrue(self.subscriber.unsubscribe_hash)

    @parameterized.expand(BATCH_PARAMS)
    def test_one_subscriber(self, idx):
        """Test that one subscriber has been registered in the ORM."""
        self.assertEqual(Subscriber.objects.count(), 1)

    @parameterized.expand(BATCH_PARAMS)
    def test_one_subreddit(self, idx):
        """Test that one subreddit has been registered in the ORM."""
        self.assertEqual(SubReddit.objects.count(), 1)

    @parameterized.expand(BATCH_PARAMS)
    def test_subscriber_str(self, idx):
        """Check str method of Subscriber."""
        self.assertIsInstance(str(self.subscriber), str)

    @parameterized.expand(SUBR_PARAMS)
    def test_subreddit_str(self, idx):
        """Check str method of SubReddit."""
        self.assertIn(str(self.subreddit), SUBREDDIT_NAMES)


class MultiCase(TestCase):
    """Subscribers with multiple subreddits."""

    def setUp(self):
        """Setup many Subscribers and SubReddits."""
        self.subreddits = SubRedditFactory.create_random_batch()
        self.subscriber = SubscriberFactory.create()
        self.subscriber.subreddits.add(*self.subreddits)

    @parameterized.expand(BATCH_PARAMS)
    def test_multiple(self, idx):
        """Check that relationship is sound."""
        for sr in self.subscriber.subreddits.all():
            self.assertTrue(sr.pk)

    @parameterized.expand(BATCH_PARAMS)
    def test_subreddit_names(self, idx):
        """Test subreddit_names method of Subscriber."""
        for name in self.subscriber.subreddit_names():
            self.assertIn(name, SUBREDDIT_NAMES)

"""Testing Subscriber and SubReddit models."""
from __future__ import unicode_literals, absolute_import

import random
from django.test import TestCase
from nose_parameterized import parameterized

from subscribers.models import Subscriber, SubReddit
from constants import SUBREDDIT_NAMES
from tests.classes import (
    SubRedditFactory,
    SubscriberFactory,
    BATCH_SIZE,
    SUBR_BATCH_SIZE,
    BATCH_PARAMS,
    SUBR_PARAMS,
)


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
        self.subreddits = SubRedditFactory.create_batch()
        self.subscribers = SubscriberFactory.create_batch(BATCH_SIZE)
        for s in self.subscribers:
            num = random.randrange(SUBR_BATCH_SIZE)
            subscription = SubReddit.objects.order_by('?')[:num]
            s.subreddits.add(*subscription)

    @parameterized.expand(BATCH_PARAMS)
    def test_multiple(self, idx):
        """Check that relationship is sound."""
        subscriber = self.subscribers[idx]
        for sr in subscriber.subreddits.all():
            self.assertTrue(sr.pk)

    @parameterized.expand(BATCH_PARAMS)
    def test_subscriber_str(self, idx):
        """Check str method of Subscriber."""
        subscriber = self.subscribers[idx]
        self.assertIsInstance(str(subscriber), str)

    @parameterized.expand(SUBR_PARAMS)
    def test_subreddit_str(self, idx):
        """Check str method of SubReddit."""
        subreddit = self.subreddits[idx]
        self.assertIn(str(subreddit), SUBREDDIT_NAMES)

    @parameterized.expand(BATCH_PARAMS)
    def test_subreddit_names(self, idx):
        """Test subreddit_names method of Subscriber."""
        subscriber = self.subscribers[idx]
        for name in subscriber.subreddit_names():
            self.assertIn(name, SUBREDDIT_NAMES)

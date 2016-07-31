"""Useful classes just for testing."""
from __future__ import unicode_literals, absolute_import
import random
from faker import Faker
from factory.django import DjangoModelFactory
import factory

from subscribers.models import Subscriber, SubReddit
from constants import SUBREDDIT_NAMES


class SubRedditFactory(DjangoModelFactory):
    """Creates SubReddit models for testing."""

    class Meta:
        """Assign SubReddit model as product of factory."""

        model = SubReddit

    display_name = factory.Iterator(SUBREDDIT_NAMES)

    @classmethod
    def create_batch(cls, **kwargs):
        """Constant batch size of all subreddits."""
        return super(SubRedditFactory, cls).create_batch(
            len(SUBREDDIT_NAMES), **kwargs)


class SubscriberFactory(DjangoModelFactory):
    """Creates Subscriber models for testing."""

    class Meta:
        """Assign Subscriber model as product of factory."""

        model = Subscriber

    email = factory.Faker('email')
    send_hour = random.randrange(24)


class FakePRAWsubreddit(object):
    """Create fake post objects."""

    display_name = ''


class FakePost(object):
    """Create fake post objects."""

    def __init__(self):
        """Initialize the post with forced unicode strings."""
        fake = Faker()
        self.subreddit = FakePRAWsubreddit()
        self.subreddit.display_name = fake.pystr(min_chars=8, max_chars=8)
        # Need more thorough unicode character range
        self.title = u'\u2018' + fake.sentence() + u'\u2019'
        self.url = fake.url()
        self.permalink = fake.url()

    @classmethod
    def create_batch(cls, size):
        """Return a list of FakePosts of length equal to given size."""
        return [cls() for _ in range(size)]

"""Useful classes just for testing."""
from __future__ import unicode_literals, absolute_import
import random
from faker import Faker
from factory.django import DjangoModelFactory
import factory

from subscribers.models import Subscriber, SubReddit
from constants import SUBREDDIT_NAMES

BATCH_SIZE = 20
BATCH_PARAMS = [(i, ) for i in range(BATCH_SIZE)]

SUBR_BATCH_SIZE = len(SUBREDDIT_NAMES)
SUBR_PARAMS = [(i, ) for i in range(SUBR_BATCH_SIZE)]
SUBR_NAME_PARAMS = [(name, ) for name in SUBREDDIT_NAMES]


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

    def __init__(self, url=None):
        """Initialize the post with forced unicode strings."""
        fake = Faker()
        self.subreddit = FakePRAWsubreddit()
        self.subreddit.display_name = fake.pystr(min_chars=8, max_chars=8)
        # Need more thorough unicode character range
        self.title = u'\u2018' + fake.sentence() + u'\u2019'
        self.url = url or fake.url()
        self.permalink = fake.url()

    @classmethod
    def create_batch(cls, size):
        """Return a list of FakePosts of length equal to given size."""
        return [cls() for _ in range(size)]

    @classmethod
    def create_batch_with_dupes(cls, size):
        """Return a list of FakePosts with some duplicates of given size."""
        if size < 2:
            raise ValueError('Batch with dupes must be at least size 2.')
        batch = [cls() for _ in range(size // 2)]
        while len(batch) < size:
            batch.append(cls(url=random.choice(batch).url))
        return batch

"""Test Deliver Cute view and user input/response."""
from __future__ import unicode_literals, absolute_import

import random
from faker import Faker
from django.test import TestCase, Client
from constants import SUBREDDIT_NAMES, EMAIL, HOME
from tests.classes import SubRedditFactory, SubscriberFactory
from subscribers.models import Subscriber

# Load form.
# Input to form.
# Redirection on success?
# Bad input
#   no email
#   incorrect email
#   select at least one subreddit?
# Good input


# Different params for POST

fake = Faker()
UNSUB = '/unsubscribe'
GOOD_PARAMS = {
    'email': fake.email(),
    'send_hour': str(random.randrange(24)),
    # 'subreddits': [str(n) for n in random.sample(
    #     range(1, len(SUBREDDIT_NAMES) + 1),
    #     random.randrange(1, len(SUBREDDIT_NAMES) + 1)
    # )],
}


class UnAuthCase(TestCase):
    """Website use case where user is not logged in."""

    def setUp(self):
        """Establish client and responses."""
        self.subreddits = SubRedditFactory.create_batch()
        self.client = Client()
        self.good_post = self.client.post(HOME, GOOD_PARAMS, follow=True)

    def test_get(self):
        """Test that front page/subscription form simply loads."""
        response = self.client.get(HOME)
        self.assertEqual(response.status_code, 200)

    def test_good_200(self):
        """Test subscribers register properly in database with good params."""
        self.assertEqual(self.good_post.status_code, 200)

    def test_good_req_fields(self):
        """Test that all required fields are filled in for good post."""
        self.assertNotIn(b'This field is required', self.good_post.content)

    def test_good_valid_input(self):
        """Test that input data is valid for good post."""
        self.assertNotIn(b'Select a valid choice.', self.good_post.content)

    def test_good_add_row(self):
        """Test that a new Subscriber has been entered into the database."""
        new_subscriber = Subscriber.objects.get(email=GOOD_PARAMS['email'])
        self.assertTrue(new_subscriber.pk)


class AlreadySubscribedCase(TestCase):
    """Website use case where user is not logged in."""

    def setUp(self):
        """Establish client and responses."""
        self.subreddits = SubRedditFactory.create_batch()
        self.subscriber = SubscriberFactory.create(email=EMAIL)
        self.subscriber.subreddits.add(*self.subreddits)
        self.client = Client()
        self.unsub_response = self.client.get(
            UNSUB, {'email': self.subscriber.email})

    def test_unsubscribe_status(self):
        """Check that unsubscribe redirects to successful unsubscribe page."""
        self.assertEqual(self.unsub_response.status_code, 200)

    def test_unsubscribe(self):
        """Check that user is deleted on unsubscriber."""
        with self.assertRaises(Subscriber.DoesNotExist):
            Subscriber.objects.get(email=self.subscriber.email)

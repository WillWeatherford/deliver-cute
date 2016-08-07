"""Test Deliver Cute view and user input/response."""
from __future__ import unicode_literals, absolute_import

import random
from faker import Faker
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from constants import SUBREDDIT_NAMES, EMAIL
from tests.classes import BATCH_SIZE, SubRedditFactory, SubscriberFactory
from subscribers.models import Subscriber
from nose_parameterized import parameterized

HOME = reverse('home')
SUCCESS_NEW = reverse('success', args=('new',))

# Load form.
# Input to form.
# Redirection on success
# Bad input
#   no email
#   incorrect email
#   select at least one subreddit?
#   bad unsubscribe hash
# Different params for POST
# unsubscribe only some of many users


# parameterize by iterating over sets of input params
def good_params():
    """Generate good parameters to post on main form."""
    fake = Faker()
    for _ in range(BATCH_SIZE):
        params = {'email': fake.email(),
                  'send_hour': str(random.randrange(24)),
                  'subreddits': [],
                  }
        yield (params, )


class UnAuthCase(TestCase):
    """Website use case where user is not logged in."""

    def setUp(self):
        """Establish client and responses."""
        self.subreddits = SubRedditFactory.create_random_batch()
        self.client = Client()

    def tearDown(self):
        """Delete all users to re-use good params."""
        for subscriber in Subscriber.objects.all():
            subscriber.delete()

    def test_get(self):
        """Test that front page/subscription form simply loads."""
        response = self.client.get(HOME)
        self.assertEqual(response.status_code, 200)

    @parameterized.expand(good_params)
    def test_good_post_redirect(self, params):
        """Test subscribers register properly in database with good params."""
        response = self.client.post(HOME, params, follow=True)
        self.assertRedirects(response, SUCCESS_NEW, status_code=302)

    @parameterized.expand(good_params)
    def test_good_post_200(self, params):
        """Test subscribers register properly in database with good params."""
        response = self.client.post(HOME, params, follow=True)
        self.assertEqual(response.status_code, 200)

    @parameterized.expand(good_params)
    def test_good_req_fields(self, params):
        """Test that all required fields are filled in for good post."""
        response = self.client.post(HOME, params, follow=True)
        self.assertNotIn(b'This field is required', response.content)

    @parameterized.expand(good_params)
    def test_good_valid_input(self, params):
        """Test that input data is valid for good post."""
        response = self.client.post(HOME, params, follow=True)
        self.assertNotIn(b'Select a valid choice.', response.content)

    @parameterized.expand(good_params)
    def test_good_add_row(self, params):
        """Test that a new Subscriber has been entered into the database."""
        self.client.post(HOME, params, follow=True)
        new_subscriber = Subscriber.objects.get(email=params['email'])
        self.assertTrue(new_subscriber.pk)


class AlreadySubscribedCase(TestCase):
    """Website use case where user is trying to unsubscribe."""

    def setUp(self):
        """Establish client and responses."""
        self.subreddits = SubRedditFactory.create_random_batch()
        self.subscriber = SubscriberFactory.create()
        self.subscriber.subreddits.add(*self.subreddits)
        self.unsub_url = reverse(
            'unsubscribe',
            args=(self.subscriber.unsubscribe_hash, )
        )
        self.client = Client()

    def tearDown(self):
        """Delete all users to re-use good params."""
        for subscriber in Subscriber.objects.all():
            subscriber.delete()

    def test_update(self):
        """Test that Subscriber information is updated on re-post of email."""
        params = {
            'email': self.subscriber.email,
            'send_hour': random.randrange(24),
        }
        self.client.post(HOME, params, follow=True)
        self.assertEqual(
            Subscriber.objects.filter(email=self.subscriber.email).count(), 1
        )

    def test_unsubscribe_status(self):
        """Check that unsubscribe redirects to successful unsubscribe page."""
        response = self.client.get(self.unsub_url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_unsubscribe_redirected(self):
        """Check that user is redirected to front page on successful unsub."""
        response = self.client.post(self.unsub_url, follow=True)
        self.assertRedirects(response, HOME, status_code=302)

    def test_unsubscribe_deleted(self):
        """Check that user is deleted on unsubscriber."""
        response = self.client.post(self.unsub_url, follow=True)
        with self.assertRaises(Subscriber.DoesNotExist):
            Subscriber.objects.get(pk=self.subscriber.pk)

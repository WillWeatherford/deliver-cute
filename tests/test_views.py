"""Test Deliver Cute view and user input/response."""
from __future__ import unicode_literals, absolute_import

import random
from faker import Faker
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from constants import SUBREDDIT_NAMES, EMAIL, HOME
from tests.classes import BATCH_SIZE, SubRedditFactory, SubscriberFactory
from subscribers.models import Subscriber
from nose_parameterized import parameterized

# Load form.
# Input to form.
# Redirection on success
# Bad input
#   no email
#   incorrect email
#   select at least one subreddit?
# Different params for POST


def good_params():
    """Generate good parameters to post on main form."""
    fake = Faker()
    for _ in range(BATCH_SIZE):
        params = {'email': fake.email(),
                  'send_hour': str(random.randrange(24)),
                  'subreddits': [],
                  }
        yield (params, )

# GOOD_PARAMS = {
#     'email': fake.email(),
#     'send_hour': str(random.randrange(24)),
#     # 'subreddits': [str(n) for n in random.sample(
#     #     range(1, len(SUBREDDIT_NAMES) + 1),
#     #     random.randrange(1, len(SUBREDDIT_NAMES) + 1)
#     # )],
# }


#parameterize by iterating over sets of input params


class UnAuthCase(TestCase):
    """Website use case where user is not logged in."""

    def setUp(self):
        """Establish client and responses."""
        self.subreddits = SubRedditFactory.create_random_batch()
        self.client = Client()
        # self.good_post = self.client.post(HOME, GOOD_PARAMS, follow=True)

    def tearDown(self):
        """Delete all users to re-use good params."""
        for subscriber in Subscriber.objects.all():
            subscriber.delete()

    def test_get(self):
        """Test that front page/subscription form simply loads."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    @parameterized.expand(good_params)
    def test_good_200(self, params):
        """Test subscribers register properly in database with good params."""
        response = self.client.post(reverse('home'), params, follow=True)
        self.assertEqual(response.status_code, 200)

    @parameterized.expand(good_params)
    def test_good_req_fields(self, params):
        """Test that all required fields are filled in for good post."""
        response = self.client.post(reverse('home'), params, follow=True)
        self.assertNotIn(b'This field is required', response.content)

    @parameterized.expand(good_params)
    def test_good_valid_input(self, params):
        """Test that input data is valid for good post."""
        response = self.client.post(reverse('home'), params, follow=True)
        self.assertNotIn(b'Select a valid choice.', response.content)

    # def test_good_add_row(self):
    #     """Test that a new Subscriber has been entered into the database."""
    #     new_subscriber = Subscriber.objects.get(email=GOOD_PARAMS['email'])
    #     self.assertTrue(new_subscriber.pk)


        #test update  instead of crete when subsc already exists

class AlreadySubscribedCase(TestCase):
    """Website use case where user is trying to unsubscribe."""

    def setUp(self):
        """Establish client and responses."""
        self.subreddits = SubRedditFactory.create_random_batch()
        self.subscriber = SubscriberFactory.create(email=EMAIL)
        self.subscriber.subreddits.add(*self.subreddits)
        self.unsub_url = reverse(
            'unsubscribe',
            args=(self.subscriber.unsubscribe_hash, )
        )
        self.client = Client()
        self.unsub_get = self.client.get(self.unsub_url, follow=True)
        self.unsub_post = self.client.post(self.unsub_url, follow=True)

    def tearDown(self):
        """Delete all users to re-use good params."""
        for subscriber in Subscriber.objects.all():
            subscriber.delete()

    def test_unsubscribe_status(self):
        """Check that unsubscribe redirects to successful unsubscribe page."""
        self.assertEqual(self.unsub_get.status_code, 200)

    def test_unsubscribe_redirected(self):
        """Check that user is redirected to front page on successful unsub."""
        self.assertRedirects(self.unsub_post, reverse('home'), status_code=302)

    def test_unsubscribe_deleted(self):
        """Check that user is deleted on unsubscriber."""
        with self.assertRaises(Subscriber.DoesNotExist):
            Subscriber.objects.get(pk=self.subscriber.pk)

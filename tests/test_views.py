"""Test Deliver Cute view and user input/response."""
from __future__ import unicode_literals, absolute_import
from django.test import TestCase, Client


# Load form.
# Input to form.
# Redirection on success?
# Bad input
#   no email
#   incorrect email
#   select at least one subreddit?
# Good input


# Different params for POST

HOME = '/'


class UnAuthCase(TestCase):
    """Website use case where user is not logged in."""

    def setUp(self):
        """Establish client and responses."""
        self.client = Client()

    def test_load(self):
        """Test that front page/subscription form simply loads."""
        response = self.client.get(HOME)
        self.assertEqual(response.status_code, 200)

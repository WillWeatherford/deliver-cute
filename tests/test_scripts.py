"""Test functions for deliver_cute project."""
from __future__ import unicode_literals, absolute_import

import pytest
import random
from string import ascii_letters, digits
from itertools import product, chain
from django.test import TestCase
from nose_parameterized import parameterized

from on_schedule import fix_image_links, htmlize_posts
from constants import SUBREDDIT_NAMES, LIMIT, EMAIL
from tests.classes import (
    FakePost,
    SubscriberFactory,
    SubRedditFactory,
)

try:
    UNICODE = unicode
    print('Python 2, using unicode class.')
except NameError:
    UNICODE = str
    print('Python 3, using str class.')

# TODO
# test unicode status of incoming PRAW post objects
# test encoding of outgoing email
# edge cases:
#   no subscribers
#   no subreddits
#   no posts
#   bad links


CUTE_POSTS = []
FIXED_LINKS = list(fix_image_links(CUTE_POSTS))

WILL_EMAIL = 'weatherford.william@gmail.com'
SUBJECT = 'TEST EMAIL'
BODY = '''
<html>
<h1>Test Header</h1>
<p>can't not apostrophe</p>
<img src="http://i.imgur.com/URw6C0c.jpg">
</html>
'''

PROTO = ('http://', 'https://')
DOMAIN = ('i.imgur.com/', )
HASH = ''.join(random.sample(ascii_letters + digits, 8))
EXT = ('.jpg', '.gifv', '.gif', '.png', )

BAD_DOMAIN = ('www.imgur.com/', 'reddit.com/', 'gfycat.com/')
BAD_EXT = ('', )

GOOD_URLS = product(PROTO, DOMAIN, HASH, EXT)
BAD_URLS = product(PROTO, BAD_DOMAIN, HASH, BAD_EXT)


FAKE_POSTS = FakePost.create_batch(20)
HTMLIZED_POSTS = ((post, ) for post in htmlize_posts(FAKE_POSTS))
FAKE_POST_ATTRS = (
    (attr, ) for attr in chain(
        *((p.title, p.url, p.permalink, p.subreddit.display_name)
          for p in FAKE_POSTS)
    )
)


class DebugCase(TestCase):
    """Run full on_schedule script in debug mode."""

    def setUp(self):
        """Setup debug user with project email."""
        self.subreddits = SubRedditFactory.create_batch()
        self.subscriber = SubscriberFactory.create(email=EMAIL)
        self.subscriber.subreddits.add(*self.subreddits)

    def test_main(self):
        """Test the main() function of on_schedule.py in debug mode."""
        from on_schedule import main
        self.assertEqual(main(True), 1)


class FakePostsCase(TestCase):
    """Using fake posts to test unicode and html escaping."""

    @parameterized.expand(FAKE_POST_ATTRS)
    def test_unicode(self, attr):
        """Ensure that all posts are unicode."""
        self.assertIsInstance(attr, UNICODE)

    @parameterized.expand(HTMLIZED_POSTS)
    def test_htmlize(self, post):
        """Test that htmlize runs without breaking."""
        self.assertIsInstance(post, UNICODE)


class RedditAPICase(TestCase):
    """Test retrieval of posts from reddit API."""

    def setUp(self):
        """Get post data to test."""


class CheckURLCase(TestCase):
    """Test URL matching regexes."""

    def setUp(self):
        """Get regex pattern."""
        from on_schedule import SRC_PAT
        self.regex = SRC_PAT

    @parameterized.expand((url, ) for url in GOOD_URLS)
    def test_src_pat_good(self, url):
        """Confirm that link regex works as expected for good urls."""
        self.assertIsNotNone(self.regex.match(''.join(url)))

    @parameterized.expand((url, ) for url in BAD_URLS)
    def test_src_pat_bad(self, url):
        """Confirm that link regex works as expected for bad urls."""
        self.assertIsNone(self.regex.match(''.join(url)))

    # def test_cute_links_source(fixed_link):
    #     """Confirm that links fixed by source fixer match the expected pattern."""
    #     assert self.regex.match(fixed_link.url) is not None


# @pytest.fixture(params=CUTE_POSTS)
# def cute_post(request):
#     """Generate cute links directly from source."""
#     return request.param


# @pytest.fixture(params=FIXED_LINKS)
# def fixed_link(request):
#     """Generate link fixed by having correct source url."""
#     return request.param


# def test_emai():
#     """Test sending an email."""
#     from on_schedule import send_email
#     send_email(WILL_EMAIL, WILL_EMAIL, [WILL_EMAIL], SUBJECT, BODY)


# def test_moonmoon():
#     """Test html escaping problems."""
#     import praw
#     from on_schedule import (
#         send_email,
#         htmlize_posts,
#         USER_AGENT,
#     )
#     reddit = praw.Reddit(user_agent=USER_AGENT)
#     moonmoon_post = reddit.get_submission(submission_id='4spncq')
#     body = '<html>' + next(htmlize_posts((moonmoon_post, ))) + '</html>'
#     send_email(WILL_EMAIL, WILL_EMAIL, [WILL_EMAIL], 'ESCAPE TEST', body)


# def test_cute_posts(cute_post):
#     """Test generating links."""
#     assert cute_post.url.startswith('http')


# def test_cute_posts_count():
#     """Test that number of links is at or under the limit per subreddit."""
#     assert len(CUTE_POSTS) <= len(SUBREDDIT_NAMES) * LIMIT


# def test_cute_posts_dupes():
#     """Test that number of links is at or under the limit per subreddit."""
#     from on_schedule import dedupe_posts
#     duplicated_posts = CUTE_POSTS + CUTE_POSTS
#     deduplicated_urls = [post.url for post in dedupe_posts(duplicated_posts)]
#     deduplicated_urls = list(sorted(deduplicated_urls))
#     urls = list(sorted(set(post.url for post in CUTE_POSTS)))
#     assert deduplicated_urls == urls




"""Test functions for deliver_cute project."""

import pytest
import random
import factory
from string import ascii_letters, digits
from itertools import product
from on_schedule import fix_image_links, SRC_PAT
from constants import SUBREDDIT_NAMES, LIMIT
from django.test import TestCase
# from subscribers.models import Subscriber, SubReddit
from nose_parameterized import parameterized

# TODO
# test htmlization
# Fake post factory
# test unicode status of incoming PRAW post objects

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


class RedditAPICase(TestCase):
    """Test retrieval of posts from reddit API."""

    def setUp(self):
        """Get post data to test."""



class CheckURLCase(TestCase):
    """Test URL matching regexes."""

    @parameterized.expand((url, ) for url in GOOD_URLS)
    def test_src_pat_good(self, url):
        """Confirm that link regex works as expected for good urls."""
        self.assertIsNotNone(SRC_PAT.match(''.join(url)))

    @parameterized.expand((url, ) for url in BAD_URLS)
    def test_src_pat_bad(self, url):
        """Confirm that link regex works as expected for bad urls."""
        self.assertIsNone(SRC_PAT.match(''.join(url)))

    # def test_cute_links_source(fixed_link):
    #     """Confirm that links fixed by source fixer match the expected pattern."""
    #     assert SRC_PAT.match(fixed_link.url) is not None


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




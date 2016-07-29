"""Test functions for deliver_cute project."""

import pytest
import random
import factory
from string import ascii_letters, digits
from itertools import product
from on_schedule import gather_posts, fix_image_links
from constants import SUBREDDIT_NAMES, LIMIT
from django.test import TestCase
from .models import Subscriber, SubReddit
from factory.django import DjangoModelFactory

# TODO
# test htmlization
# test unicode status

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
HASH = ''.join(random.choice(ascii_letters + digits) for _ in range(8))
EXT = ('.jpg', '.gifv', '.gif', '.png', )

BAD_DOMAIN = ('www.imgur.com/', 'reddit.com/', 'gfycat.com/')
BAD_EXT = ('', )


class RedditAPICase(TestCase):
    """Test retrieval of posts from reddit API."""

    def setUp(self):
        self.posts = list(gather_posts(SUBREDDIT_NAMES, LIMIT))



@pytest.fixture(params=product(PROTO, DOMAIN, HASH, EXT))
def good_src_url(request):
    """Generate good imgur source urls."""
    return ''.join(request.param)


@pytest.fixture(params=product(PROTO, BAD_DOMAIN, HASH, BAD_EXT))
def bad_src_url(request):
    """Generate bad source urls."""
    return ''.join(request.param)


@pytest.fixture(params=CUTE_POSTS)
def cute_post(request):
    """Generate cute links directly from source."""
    return request.param


@pytest.fixture(params=FIXED_LINKS)
def fixed_link(request):
    """Generate link fixed by having correct source url."""
    return request.param


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


def test_cute_posts(cute_post):
    """Test generating links."""
    assert cute_post.url.startswith('http')


def test_cute_posts_count():
    """Test that number of links is at or under the limit per subreddit."""
    assert len(CUTE_POSTS) <= len(SUBREDDIT_NAMES) * LIMIT


def test_cute_posts_dupes():
    """Test that number of links is at or under the limit per subreddit."""
    from on_schedule import dedupe_posts
    duplicated_posts = CUTE_POSTS + CUTE_POSTS
    deduplicated_urls = [post.url for post in dedupe_posts(duplicated_posts)]
    deduplicated_urls = list(sorted(deduplicated_urls))
    urls = list(sorted(set(post.url for post in CUTE_POSTS)))
    assert deduplicated_urls == urls


def test_src_pat_good(good_src_url):
    """Confirm that link regex works as expected for good urls."""
    from on_schedule import SRC_PAT
    assert SRC_PAT.match(good_src_url) is not None


def test_src_pat_bad(bad_src_url):
    """Confirm that link regex works as expected for bad urls."""
    from on_schedule import SRC_PAT
    assert SRC_PAT.match(bad_src_url) is None


def test_cute_links_source(fixed_link):
    """Confirm that links fixed by source fixer match the expected pattern."""
    from on_schedule import SRC_PAT
    assert SRC_PAT.match(fixed_link.url) is not None

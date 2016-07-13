"""Test functions for deliver_cute project."""

import pytest
import random
from string import ascii_letters, digits
from itertools import product
from deliver_cute import gather_cute_posts, fix_image_links, CUTE_SUBS, LIMIT

CUTE_POSTS = gather_cute_posts(CUTE_SUBS, LIMIT)
FIXED_LINKS = fix_image_links(CUTE_POSTS)

WILL_EMAIL = 'weatherford.william@gmail.com'
SUBJECT = 'TEST EMAIL'
BODY = '''
<html>
<h1>Test Header</h1>

<img src="http://i.imgur.com/URw6C0c.jpg">
</html>
'''

PROTO = ('http://', 'https://')
DOMAIN = ('i.imgur.com/', )
HASH = ''.join(random.choice(ascii_letters + digits) for _ in range(8))
EXT = ('.jpg', '.gifv', '.gif', '.png', )

BAD_DOMAIN = ('www.imgur.com/', 'reddit.com/', )
BAD_HASH = ''.join(random.choice(ascii_letters + digits) for _ in range(8))
BAD_EXT = ('', )


@pytest.fixture(params=product(PROTO, DOMAIN, HASH, EXT))
def good_src_url(request):
    """Generate good imgur source urls."""
    return ''.join(request.param)


@pytest.fixture(params=product(PROTO, BAD_DOMAIN, BAD_HASH, BAD_EXT))
def bad_src_url(request):
    """Generate good imgur source urls."""
    return ''.join(request.param)


@pytest.fixture(params=CUTE_POSTS)
def cute_post(request):
    """Generate cute links directly from source."""
    return request.param


@pytest.fixture(params=FIXED_LINKS)
def fixed_link(request):
    """Generate link fixed by having correct source url."""
    return request.param


def test_email_gmail():
    """Test sending an email."""
    from deliver_cute import send_email_from_gmail
    send_email_from_gmail(WILL_EMAIL, WILL_EMAIL, SUBJECT, BODY)


def test_cute_links(cute_post):
    """Test generating links."""
    assert cute_post.url.startswith('http')


def test_cute_links_count():
    """Test that number of links is at or under the limit per subreddit."""
    assert len(list(CUTE_POSTS)) <= len(CUTE_SUBS) * LIMIT


def test_src_pat_positive(good_src_url):
    """Confirm that link regex works as expected."""
    from deliver_cute import SRC_PAT
    assert SRC_PAT.match(good_src_url) is not None


def test_src_pat_negative(bad_src_url):
    """Confirm that link regex works as expected."""
    from deliver_cute import SRC_PAT
    assert SRC_PAT.match(bad_src_url) is None


def test_cute_links_source(fixed_link):
    """Confirm that links fixed by source fixer match the expected pattern."""
    from deliver_cute import SRC_PAT
    assert SRC_PAT.match(fixed_link)

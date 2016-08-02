"""Test functions for deliver_cute project."""
from __future__ import unicode_literals, absolute_import

import random
from string import ascii_letters, digits
from itertools import product
from django.test import TestCase
from django.core import mail
from nose_parameterized import parameterized

from on_schedule import fix_image_links
from constants import SUBREDDIT_NAMES, LIMIT, EMAIL
from tests.classes import (
    FakePost,
    SubscriberFactory,
    SubRedditFactory,
    BATCH_SIZE,
    BATCH_PARAMS,
    # SUBR_BATCH_SIZE,
    # SUBR_PARAMS,
    SUBR_NAME_PARAMS,
)

try:
    UNICODE = unicode
    print('Python 2, using unicode class.')
except NameError:
    UNICODE = str
    print('Python 3, using str class.')

# TODO
# test unicode status of incoming PRAW post objects
# test encoding of outgoing html
#   test fix_urls
#       make some bad urls
#   test sort_urls
#   test subscribers_for_now
#   test email outbox

# edge cases:
#   unsorted
#   already sorted
#   no subscribers
#   no subreddits
#   no posts
#   bad links
#   limit 0
#   very high limit


CUTE_POSTS = []
FIXED_LINKS = list(fix_image_links(CUTE_POSTS))
SUBJECT = 'DEBUG'
TEXT = 'Plain text message.'
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


class EmailCase(TestCase):
    """Testing sending of email."""

    def setUp(self):
        """Send an email."""
        mail.send_mail(
            SUBJECT, TEXT, EMAIL, [EMAIL],
            html_message=BODY,
            fail_silently=False,
        )

    def test_outbox(self):
        """Test sending an email."""
        self.assertEqual(len(mail.outbox), 1)

    def test_subject(self):
        """Test sending an email."""
        email = mail.outbox[0]
        self.assertEqual(SUBJECT, email.subject)


class RedditAPICase(TestCase):
    """Test retrieval of posts from reddit API."""

    def setUp(self):
        """Get post data to test."""
        from on_schedule import create_post_map
        # test with different limits
        self.no_posts = create_post_map([], LIMIT)
        self.all_posts = create_post_map(SUBREDDIT_NAMES, LIMIT)

    def test_no_subreddits(self):
        """Confirm that zero subreddits returns an empty dictionary."""
        self.assertEqual(self.no_posts, {})

    def test_dictionary(self):
        """Confirm that given subreddits returns a dictionary."""
        self.assertIsInstance(self.all_posts, dict)

    @parameterized.expand(SUBR_NAME_PARAMS)
    def test_cute_posts(self, name):
        """Test that gathered posts have links."""
        for post in self.all_posts[name]:
            self.assertTrue(post.url.startswith('http'))

    @parameterized.expand(SUBR_NAME_PARAMS)
    def test_cute_posts_count(self, name):
        """Test that number of links is at or under the limit per subreddit."""
        self.assertLessEqual(len(self.all_posts[name]), LIMIT)


class FakePostsCase(TestCase):
    """Using fake posts to test unicode and html escaping."""

    def setUp(self):
        """Set up fake_posts."""
        from on_schedule import htmlize_posts, get_email_body
        self.subscriber = SubscriberFactory.create(email=EMAIL)
        self.posts = FakePost.create_batch(BATCH_SIZE)
        self.htmlized_posts = list(htmlize_posts(self.posts))
        self.email_body = get_email_body(self.subscriber, self.htmlized_posts)
        # import pdb;pdb.set_trace()
        self.duplicates = FakePost.create_batch_with_dupes(BATCH_SIZE)

    @parameterized.expand(BATCH_PARAMS)
    def test_unicode(self, idx):
        """Ensure that all FakePost attributes are unicode."""
        p = self.posts[idx]
        for attr in (p.title, p.url, p.permalink, p.subreddit.display_name):
            self.assertIsInstance(attr, UNICODE)

    @parameterized.expand(BATCH_PARAMS)
    def test_htmlize_unicode(self, idx):
        """Test that htmlize runs without breaking."""
        post = self.htmlized_posts[idx]
        self.assertIsInstance(post, UNICODE)

    @parameterized.expand(BATCH_PARAMS)
    def test_html_post_contains(self, idx):
        """Ensure that all FakePost attributes are unicode."""
        p = self.posts[idx]
        hp = self.htmlized_posts[idx]
        for attr in (p.title, p.url, p.permalink, p.subreddit.display_name):
            self.assertIn(attr, hp)

    @parameterized.expand(BATCH_PARAMS)
    def test_html_body_contains(self, idx):
        """Ensure that all FakePost attributes are unicode."""
        hp = self.htmlized_posts[idx]
        self.assertIn(hp, self.email_body)

    def test_html_body_unsub_link(self):
        """Ensure that all FakePost attributes are unicode."""
        self.assertIn(
            '/unsubscribe/{}'.format(self.subscriber.pk),
            self.email_body
        )

    def test_dedupe_posts(self):
        """Test that urls of deduped posts is equal to set of those urls."""
        from on_schedule import dedupe_posts
        deduped_urls = [post.url for post in dedupe_posts(self.duplicates)]
        self.assertEqual(
            list(sorted(deduped_urls)),
            list(sorted(set(deduped_urls)))
        )

    # test html escaping by checking for &quot, \u2018 etc.


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


# @pytest.fixture(params=FIXED_LINKS)
# def fixed_link(request):
#     """Generate link fixed by having correct source url."""
#     return request.param

#


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


class DebugCase(TestCase):
    """Run full on_schedule script in debug mode."""

    def setUp(self):
        """Add debug user with project email to test database."""
        from on_schedule import main
        self.subreddits = SubRedditFactory.create_batch()
        self.subscriber = SubscriberFactory.create(email=EMAIL)
        self.subscriber.subreddits.add(*self.subreddits)
        self.result = main(True)

    def test_main(self):
        """Test the main() function of on_schedule.py in debug mode."""
        self.result = self.assertEqual(self.result, 1)

    def test_outbox(self):
        """Test sending an email."""
        self.assertEqual(len(mail.outbox), 1)

    def test_recipient(self):
        """Test sending an email."""
        email = mail.outbox[0]
        self.assertEqual(self.subscriber.email, email.to[0])

    def test_unsubscribe_link(self):
        """Test sending an email."""
        email = mail.outbox[0]
        self.assertIn(
            b'/unsubscribe/' + str(self.subscriber.pk).encode('ascii'),
            email.alternatives,
        )

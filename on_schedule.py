#!/usr/bin/python
"""
Cuteness Delivery System.

This program requests the top links from various subreddits of cute animals
and email them to participants.
"""
from __future__ import unicode_literals, absolute_import

import re
import sys
import praw
import django
import calendar
import requests
from pytz import timezone
from bs4 import BeautifulSoup
from operator import attrgetter
from datetime import date, datetime
from constants import LIMIT, EMAIL
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
django.setup()
from subscribers.models import Subscriber

USER_AGENT = 'python:deliver_cute:v1.0 (by /u/____OOOO____)'
TXT_CONTENT = 'Plain text message.'
EMAIL_SUBJECT_TEMPLATE = '{debug}Cute Pics for {d}, {m} {i} {y}'
FROM_NAME = 'Deliver Cute'
PIC_WIDTH = '400'

YT_PAT = re.compile(r'.*(youtu\.be|youtube\.com).*')
SRC_PAT = re.compile(r'http(s)?://i\.(imgur|reddituploads|redd).*\.[a-z]{3,4}')


def main(debug):
    """Gather then email top cute links."""
    subscribers = subscribers_for_now(debug)
    if not subscribers:
        print('0 subscribers want cute delivered at {}'.format(get_now_hour()))
        return 0

    subject = get_email_subject(debug)

    reddit = praw.Reddit(user_agent=USER_AGENT)

    sent_count = 0
    post_map = {}
    found_posts = set()
    for subscriber in subscribers:
        posts_to_send = []
        for name in subscriber.subreddit_names():
            try:
                posts_to_send.extend(post_map[name])
            except KeyError:
                posts = get_posts_from_reddit(reddit, name, LIMIT)
                posts = fix_image_links(posts)
                posts = dedupe_posts(posts, found_posts)
                posts = list(posts)
                post_map[name] = posts
                posts_to_send.extend(posts)

        posts_to_send = sort_posts(posts_to_send)
        posts_to_send = htmlize_posts(posts_to_send)
        body = get_email_body(subscriber, posts_to_send)
        sent_count += send_email(subject, subscriber, body)
        print('Email sent to {}...'.format(subscriber.email))
    return sent_count


def get_now_hour():
    """Return an integer of the current hour in Pacific Standard Time."""
    now = datetime.now(tz=timezone('US/Pacific'))
    return now.hour


def subscribers_for_now(debug):
    """Collect subscribers with send_hour set to current time."""
    if debug:
        return Subscriber.objects.filter(email=EMAIL)
    return Subscriber.objects.filter(send_hour=get_now_hour())


def get_posts_from_reddit(reddit, subreddit_name, limit):
    """Get subreddit names from given subreddit name."""
    subreddit = reddit.get_subreddit(subreddit_name)
    return subreddit.get_top_from_day(limit=limit)


def get_relevant_posts(post_map, subscriber):
    """Filter only those posts selected by the current subscriber."""
    for subreddit_name in subscriber.subreddit_names():
        for post in post_map[subreddit_name]:
            yield post


def dedupe_posts(posts, found_posts):
    """Generate posts where duplicates have been removed by comparing url."""
    for post in posts:
        if post.url not in found_posts:
            yield post
            found_posts.add(post.url)
        else:
            print('Omitting duplicate {}'.format(post.url))


def sort_posts(posts):
    """Generate posts sorted by their upvote count."""
    for post in sorted(posts, key=attrgetter('score'), reverse=True):
        yield post


def fix_image_links(posts):
    """Make sure that each imgur link is directly to the content."""
    for post in posts:
        link = post.url
        if YT_PAT.match(link):
            continue

        # Temporary measure until able to display gifv and gyfcat properly
        if link.endswith('gifv') or link.endswith('mp4') or 'gfycat' in link:
            continue

        if not SRC_PAT.match(link):
            try:
                link = find_source_link(link)
            except AttributeError as e:
                print('Error trying to get img src at {}: {}'.format(link, e))
                continue
        link = re.sub(r'^//', 'http://', link)
        post.url = link
        yield post


def find_source_link(link):
    """Scrape the direct source link from imgur or other website."""
    # Currently only works for imgur
    response = requests.get(link)
    html = BeautifulSoup(response.text, 'html.parser')
    div = html.find('div', class_='post-image')
    img = div.find('img')
    return img.attrs['src']


def htmlize_posts(posts):
    """Generate each link as an html-ized image element."""
    for post in posts:
        subreddit = post.subreddit.display_name
        context = {
            'subreddit': subreddit,
            'subreddit_name': '/r/' + subreddit,
            'subreddit_url': 'https://www.reddit.com/r/' + subreddit,
            'title': post.title,
            'url': post.url,
            'permalink': post.permalink,
            'width': PIC_WIDTH,
        }
        yield render_to_string('image.html', context=context)


def get_email_body(subscriber, posts):
    """Format posts into HTML."""
    context = {
        'posts': posts,
        'subscriber': subscriber,
        'site_url': settings.SITE_URL,
    }
    return render_to_string('daily_email.html', context=context)


def get_email_subject(debug):
    """Format today's date into the email subject."""
    today = date.today()
    day_name = calendar.day_name[today.weekday()]
    month_name = calendar.month_name[today.month]
    return EMAIL_SUBJECT_TEMPLATE.format(
        debug='DEBUG ' * debug,
        d=day_name,
        m=month_name,
        i=today.day,
        y=today.year,
    )


def send_email(subject, subscriber, body):
    """Return number of emails sent using django mail with project specs."""
    print('Sending email to {}...'.format(subscriber.email))
    return send_mail(
        subject,
        TXT_CONTENT,
        EMAIL,
        [subscriber.email],
        html_message=body,
        fail_silently=False,
    )


if __name__ == '__main__':
    try:
        debug = bool(sys.argv[1])
    except IndexError:
        debug = False
    print('Debug is {}'.format(debug))
    print('{} email sent.'.format(main(debug)))

#!/usr/bin/python
"""
Cuteness Delivery System.

This program requests the top links from various subreddits of cute animals
and email them to participants.
"""
from __future__ import unicode_literals, absolute_import
# try:
#     from html import escape
#     print('Python 3: using html.escape()')
# except ImportError:
#     from cgi import escape
#     print('Python 2: using cgi.escape()')

import re
import sys
import praw
import django
import smtplib
import calendar
import requests
from pytz import timezone
from itertools import chain
from bs4 import BeautifulSoup
from operator import attrgetter
from datetime import date, datetime
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
from constants import LIMIT, EMAIL, APP_PASSWORD
django.setup()
from django.conf import settings
from subscribers.models import Subscriber
from django.core.mail import send_mail
from django.template.loader import render_to_string

USER_AGENT = 'python:deliver_cute:v1.0 (by /u/____OOOO____)'

EMAIL_SUBJECT_TEMPLATE = '{debug}Cute Pics for {date}'
FROM_NAME = 'Deliver Cute'
PIC_WIDTH = '400'

YT_PAT = re.compile(r'.*(youtu\.be|youtube\.com).*')
SRC_PAT = re.compile(r'http(s)?://i\.(imgur|reddituploads|redd).*\.[a-z]{3,4}')


def main(debug):
    """Gather then email top cute links."""
    subscribers = subscribers_for_now(debug)
    if not subscribers:
        now = datetime.now(tz=timezone('US/Pacific'))
        print('No subscribers want cute delivered at {}'.format(now.hour))
        return 0

    # subreddit_names = chain(*(s.subreddit_names() for s in subscribers))
    # post_map = create_post_map(subreddit_names, LIMIT)

    # server = setup_email_server(EMAIL, APP_PASSWORD)
    subject = get_email_subject(debug)

    reddit = praw.Reddit(user_agent=USER_AGENT)

    sent_count = 0
    post_map = {}
    found_posts = set()
    for subscriber in subscribers:
        subreddit_names = set(subscriber.subreddit_names()) - post_map.keys()
        # posts = get_relevant_posts(post_map, subscriber)
        posts = get_posts_from_reddit(reddit, subreddit_names, LIMIT)
        posts = fix_image_links(posts)
        posts = dedupe_posts(posts)
        posts = sort_posts(posts)
        posts = htmlize_posts(posts)
        body = get_email_body(subscriber, posts)
        sent_count += send_mail(
            subject, 'DEBUG', EMAIL, [subscriber.email],
            html_message=body,
            fail_silently=False,
            # server, EMAIL, FROM_NAME, subscriber.email, subject, body
        )

    # server.quit()
    return sent_count


def subscribers_for_now(debug):
    """Collect subscribers with send_hour set to current time."""
    if debug:
        return Subscriber.objects.filter(email=EMAIL)
    now = datetime.now(tz=timezone('US/Pacific'))
    return Subscriber.objects.filter(send_hour=now.hour)


def get_posts_from_reddit(reddit, subreddit_names, limit):
    """Get subreddit names from given subreddit name."""
    subreddit = reddit.get_subreddit(name)
    return subreddit.get_top_from_day(limit=limit)


def create_post_map(subreddit_names, limit):
    """Return dictionary with keys of subreddit names at given post limit."""
    reddit = praw.Reddit(user_agent=USER_AGENT)
    post_map = dict.fromkeys(subreddit_names)
    for name in post_map:
        subreddit = reddit.get_subreddit(name)
        new_posts = subreddit.get_top_from_day(limit=limit)
        post_map[name] = list(new_posts)
    return post_map


def get_relevant_posts(post_map, subscriber):
    """Filter only those posts selected by the current subscriber."""
    for subreddit_name in subscriber.subreddit_names():
        for post in post_map[subreddit_name]:
            yield post


def dedupe_posts(posts):
    """Generate posts where duplicates have been removed by comparing url."""
    found_already = set()
    for post in posts:
        if post.url not in found_already:
            yield post
            found_already.add(post.url)
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
    today_date_str = '{d}, {m} {i} {y}'.format(
        d=day_name,
        m=month_name,
        i=today.day,
        y=today.year,
    )
    return EMAIL_SUBJECT_TEMPLATE.format(
        debug='DEBUG ' * debug,
        date=today_date_str)


def setup_email_server(email, password):
    """Send an email using gmail's smtp server."""
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(email, password)
    return server


# def send_email(server, from_addr, from_name, to_addr, subject, body):
#     """Send an email with given server and message info."""
#     html = MIMEText(body, 'html')
#     msg = MIMEMultipart('alternative')
#     msg.attach(html)
#     msg['Subject'] = subject
#     msg['From'] = from_name
#     msg['To'] = to_addr
#     server.sendmail(from_addr, to_addr, msg.as_string())
#     print('Email send to {}'.format(to_addr))


if __name__ == '__main__':
    try:
        debug = bool(sys.argv[1])
    except IndexError:
        debug = False
    print('Debug is {}'.format(debug))
    print('{} email sent.'.format(main(debug)))

"""
Cuteness Delivery System.

This program requests the top links from various subreddits of cute animals
and email them to participants.
"""

import os
import re
import sys
import html
import praw
import smtplib
import calendar
import requests
from pytz import timezone
from itertools import chain
from bs4 import BeautifulSoup
from operator import attrgetter
from datetime import date, datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import django

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "delivercute.settings")
django.setup()
from subscribers.models import Subscriber

try:
    USERNAME = os.environ['DELIVERCUTE_EMAIL']
    PASSWORD = os.environ['DELIVERCUTE_PASSWORD']
except KeyError:
    print('Global security variables not set.')
    sys.exit()

USER_AGENT = 'python:deliver_cute:v1.0 (by /u/____OOOO____)'
LIMIT = 10

EMAIL_SUBJECT_TEMPLATE = 'Cute Pics for {}'
FROM_NAME = 'Deliver Cute'
PIC_WIDTH = 400
PIC_TEMPLATE = '''
<p>
  <p>
    <a href={permalink}>{title}</a>
    from <a href={subreddit_url}>{subreddit_name}</a>
  </p>
  <p>
    <img src="{url}" style="width:{width}px" alt={title}>
  </p>
</p>
'''

YT_PAT = re.compile(r'.*(youtu\.be|youtube\.com).*')
SRC_PAT = re.compile(r'http(s)?://i\.(imgur|reddituploads|redd).*\.[a-z]{3,4}')


def gather_posts(subreddit_names, limit):
    """Generate image urls from top links in cute subs, sorted by score."""
    reddit = praw.Reddit(user_agent=USER_AGENT)
    subreddits = (reddit.get_subreddit(name) for name in subreddit_names)
    posts = chain(*(sub.get_top_from_day(limit=limit) for sub in subreddits))
    for post in posts:
        print('sub: {} url: {}; score: {}'
              ''.format(post.subreddit, post.url, post.score))
        yield post


def dedupe_posts(posts):
    """Remove duplicate posts."""
    found_already = set()
    for post in posts:
        if post.url not in found_already:
            yield post
            found_already.add(post.url)
        else:
            print('Omitting duplicate {}'.format(post.url))


def fix_image_links(posts):
    """Make sure that each imgur link is directly to the content."""
    for post in posts:
        link = post.url
        if YT_PAT.match(link):
            print('discarding {} as youtube link'.format(link))
            continue

        # Temporary measure until able to display gifv and gyfcat properly
        if link.endswith('gifv') or 'gfycat' in link:
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


def get_email_subject():
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
    return EMAIL_SUBJECT_TEMPLATE.format(today_date_str)


def get_email_body(posts):
    """Format posts into HTML."""
    posts = htmlize_posts(posts)
    return '<html>{}</html>'.format('<br>'.join(posts))


def htmlize_posts(posts):
    """Generate each link as an html-ized image element."""
    for post in posts:
        subreddit = post.subreddit.display_name
        yield PIC_TEMPLATE.format(
            permalink=html.escape(post.permalink),
            url=html.escape(post.url),
            title=html.escape(post.title),
            subreddit_name=html.escape('/r/' + subreddit),
            subreddit_url=html.escape('https://www.reddit.com/r/' + subreddit),
            width=PIC_WIDTH,
        )


def subscribers_for_now():
    """Collect subscribers with send_hour set to current time."""
    now = datetime.now(tz=timezone('US/Pacific'))
    return Subscriber.objects.filter(send_hour=now.hour)


def setup_email_server(username, password):
    """Send an email using gmail's smtp server."""
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(USERNAME, PASSWORD)
    return server


def send_email(server, from_addr, from_name, to_addr, subject, body):
    """Send an email with given server and message info."""
    html = MIMEText(body, 'html')
    msg = MIMEMultipart('alternative')
    msg.attach(html)
    msg['Subject'] = subject
    msg['From'] = from_name
    msg['To'] = to_addr
    server.sendmail(from_addr, to_addr, msg.as_string())
    print('Email send to {}'.format(to_addr))


def create_post_map(subreddit_names, limit):
    """Create mapping of top posts to their subreddit names."""
    reddit = praw.Reddit(user_agent=USER_AGENT)
    post_map = dict.fromkeys(subreddit_names)
    for name in post_map:
        subreddit = reddit.get_subreddit(name)
        new_posts = subreddit.get_top_from_day(limit=limit)
        new_posts = fix_image_links(new_posts)
        post_map[name] = list(new_posts)
    return post_map


def get_relevant_posts(post_map, subscriber):
    """Filter only those posts selected by the current subscriber."""
    for subreddit_name in subscriber.subreddit_names():
        yield from iter(post_map[subreddit_name])


def main(to_addr):
    """Gather then email top cute links."""
    subscribers = subscribers_for_now()
    if not subscribers:
        now = datetime.now(tz=timezone('US/Pacific'))
        print('No subscribers want cute delivered at {}'.format(now.hour))
        return

    subreddit_names = chain(*(s.subreddit_names() for s in subscribers))
    post_map = create_post_map(subreddit_names, LIMIT)

    subject = get_email_subject()
    server = setup_email_server(USERNAME, PASSWORD)

    for subscriber in subscribers:
        posts = get_relevant_posts(post_map, subscriber)
        posts = dedupe_posts(posts)
        posts = sorted(posts, key=attrgetter('score'), reverse=True)
        body = get_email_body(posts)
        send_email(server, USERNAME, FROM_NAME, subscriber.email, subject, body)

    server.quit()

if __name__ == '__main__':
    try:
        to_addr = sys.argv[1]
    except IndexError:
        to_addr = USERNAME
    main(to_addr)

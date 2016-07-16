"""
Cuteness Delivery System.

This program requests the top links from various subreddits of cute animals
and email them to participants.
"""

# TODO
# Send date in email subject
# deploy

# currently incompatible media sources:
#   video tag?
#   streamable
#   gyfcat
#   gifv
#   album link on imgur

import os
import re
import sys
import html
import praw
import smtplib
import calendar
import requests
from heapq import merge
from datetime import date
from bs4 import BeautifulSoup
from operator import attrgetter
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    USERNAME = os.environ['USERNAME']
    PASSWORD = os.environ['PASSWORD']
except KeyError:
    print('Global security variables not set.')
    sys.exit()

USER_AGENT = 'python:deliver_cute:v1.0 (by /u/____OOOO____)'
CUTE_SUBS = [
    'AnimalsBeingBros',
    'AnimalsBeingConfused',
    'AnimalsBeingDerps',
    'aww',
    'awwgifs',
    'babybigcatgifs',
    'babyelephantgifs',
    'Eyebleach',
    'gifsofotters',
    'kittengifs',
    'StartledCats',
]
LIMIT = 10

EMAIL_SUBJECT_TEMPLATE = 'Cute Pics for {}'
PIC_WIDTH = 400
PIC_TEMPLATE = '''
<p>
  <p>
    <a href={url}>{title}</a>
  </p>
  <p>
    <img src="{url}" style="width:{width}px" alt={title}>
  </p>
</p>
'''

YT_PAT = re.compile(r'.*(youtu\.be|youtube\.com).*')
SRC_PAT = re.compile(r'http(s)?://i\.(imgur|reddituploads|redd).*\.[a-z]{3,4}')


def gather_cute_posts(subreddit_names, limit):
    """Generate image urls from top links in cute subs, sorted by score."""
    reddit = praw.Reddit(user_agent=USER_AGENT)
    subreddits = (reddit.get_subreddit(name) for name in subreddit_names)
    all_posts = (sub.get_top_from_day(limit=limit) for sub in subreddits)

    for post in merge(*all_posts, key=attrgetter('score'), reverse=True):
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
        yield PIC_TEMPLATE.format(
            url=html.escape(post.url),
            title=html.escape(post.title),
            width=PIC_WIDTH
        )


def send_email_from_gmail(from_addr, to_addr, subject, body):
    """Send an email using gmail's smtp server."""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = 'Deliver Cute'
    msg['To'] = to_addr
    html = MIMEText(body, 'html')
    msg.attach(html)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.login(USERNAME, PASSWORD)
    s.sendmail(from_addr, to_addr, msg.as_string())
    s.quit()


def main(to_addr):
    """Gather then email top cute links."""
    posts = gather_cute_posts(CUTE_SUBS, LIMIT)
    posts = dedupe_posts(posts)
    posts = fix_image_links(posts)
    body = get_email_body(posts)
    subject = get_email_subject()
    send_email_from_gmail(USERNAME, to_addr, subject, body)


if __name__ == '__main__':
    main(sys.argv[1])

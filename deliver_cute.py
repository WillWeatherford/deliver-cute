"""
Cuteness Delivery System.

This program requests the top links from various subreddits of cute animals
and email them to participants.
"""

# TODO
# alt text from reddit post
# link images too
# gyfcat
# gifv
# album link
# create its own email address
# deploy

import os
import re
import sys
import praw
import smtplib
import requests
from operator import attrgetter
from heapq import merge
from bs4 import BeautifulSoup
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
PIC_WIDTH = 300
YT_PAT = re.compile(r'.*(youtu\.be|youtube\.com).*')
SRC_PAT = re.compile(r'http(s)?://i\.(imgur|reddituploads|redd).*\.[a-z]{3,4}')


def gather_cute_links(subreddit_names, limit):
    """Generate image urls from top links in cute subs, sorted by score."""
    reddit = praw.Reddit(user_agent=USER_AGENT)
    subreddits = (reddit.get_subreddit(sub_name) for sub_name in subreddit_names)
    all_posts = (sub.get_top_from_day(limit=limit) for sub in subreddits)

    for post in merge(*all_posts, key=attrgetter('score'), reverse=True):
        print('url: {}; score: {}'.format(post.url, post.score))
        yield post.url


def fix_image_links(links):
    """Make sure that each imgur link is directly to the content."""
    for link in links:
        if YT_PAT.match(link):
            print('discarding {} as youtube link'.format(link))
            continue

        # Temporary measure until able to display gifv and gyfcat properly
        if link.endswith('gifv') or 'gfycat' in link:
            continue

        if not SRC_PAT.match(link):
            link = find_source_link(link)
        link = re.sub(r'^//', 'http://', link)
        yield link


def find_source_link(link):
    """Scrape the direct source link from imgur or other website."""
    response = requests.get(link)
    html = BeautifulSoup(response.text, 'html.parser')
    try:
        div = html.find('div', class_='post-image')
    except AttributeError as e:
        print('Error trying to get image div at {}: {}'.format(link, e))
    try:
        img = div.find('img')
        link = img.attrs['src']
    except AttributeError as e:
        print('Error trying to get img src at {}: {}'.format(link, e))
    return link


def htmlize_image_links(links):
    """Generate each link as an html-ized image element."""
    for link in links:
        yield '<p>{}</p><img src="{}" style="width:{}px">'.format(link, link, PIC_WIDTH)


def send_email_from_gmail(from_addr, to_addr, subject, body):
    """Send an email using gmail's smtp server."""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_addr
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
    links = gather_cute_links(CUTE_SUBS, LIMIT)
    links = fix_image_links(links)
    links = htmlize_image_links(links)
    text = '<html>' + '<br>'.join(links) + '</html>'
    send_email_from_gmail(USERNAME, to_addr, 'Cute pics', text)


if __name__ == '__main__':
    main(sys.argv[1])

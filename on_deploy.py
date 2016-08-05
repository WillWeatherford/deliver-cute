#!/usr/bin/python
"""Run commands upon deployment to set up admin user and initial subreddits."""

import os
import django
from constants import SUBREDDIT_NAMES, EMAIL, PASSWORD
django.setup()

from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from subscribers.models import SubReddit, Subscriber

# Set up admin user with project email and human-friendly password
try:
    superuser = User.objects.create_superuser('delivercute', EMAIL, PASSWORD)
    superuser.save()
except IntegrityError:
    print('delivercute superuser already in database.')

# Set up initial list of SubReddits from which to gather posts
for subreddit_name in SUBREDDIT_NAMES:
    try:
        new = SubReddit(display_name=subreddit_name)
        new.save()
    except IntegrityError:
        print('SubReddit {} already in database.'.format(subreddit_name))


# Set up Subscriber with project email for debugging
debug_sub, created = Subscriber.objects.get_or_create(
    email=EMAIL,
    defaults={'email': EMAIL, 'send_hour': 0},
)
if created:
    debug_sub.subreddits.add(*SubReddit.objects.all())

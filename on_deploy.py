#!/usr/bin/python
"""Run commands upon deployment to set up admin user and initial subreddits."""

import os
import sys
import django
django.setup()

import on_schedule
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from subscribers.models import SubReddit, Subscriber


SUBREDDIT_NAMES = [
    'StartledCats',
    'kittengifs',
    'gifsofotters',
    'Eyebleach',
    'babyelephantgifs',
    'babybigcatgifs',
    'awwgifs',
    'AnimalsBeingConfused',
    'AnimalsBeingDerps',
    'AnimalsBeingBros',
    'aww',
    'rarepuppers',
]

# Get project email and human-friendly password from environment
try:
    EMAIL = os.environ['DELIVERCUTE_EMAIL']
    PASSWORD = os.environ['DELIVERCUTE_PASSWORD_BASIC']
except KeyError:
    print('Global security variables not set.')
    sys.exit()


# Set up admin user with project email and human-friendly password
try:
    superuser = User.objects.create_superuser('delivercute', EMAIL, PASSWORD)
    superuser.save()
except IntegrityError:
    print('delivercute superuser already in database.')


# Set up Subscriber with project email for debugging
try:
    debug_sub = Subscriber(email=EMAIL, send_hour=0)
    debug_sub.save()
    debug_sub.subreddits.add(*SubReddit.objects.all())
except IntegrityError:
    print('delivercute subscriber already in database.')


# Set up initial list of SubReddits from which to gather posts
for subreddit_name in SUBREDDIT_NAMES:
    try:
        new = SubReddit(display_name=subreddit_name)
        new.save()
    except IntegrityError:
        print('SubReddit {} already in database.'.format(subreddit_name))


# Send a test run of the program in debug mode
on_schedule.main(True)

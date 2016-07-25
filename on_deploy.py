#!/usr/bin/python
"""Run commands upon deployment to set up admin user and initial subreddits."""

import os
import sys
import django
django.setup()

from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from subscribers.models import SubReddit

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

try:
    EMAIL = os.environ['DELIVERCUTE_EMAIL']
    PASSWORD = os.environ['DELIVERCUTE_PASSWORD_BASIC']
except KeyError:
    print('Global security variables not set.')
    sys.exit()

try:
    superuser = User.objects.create_superuser('delivercute', EMAIL, PASSWORD)
    superuser.save()
except IntegrityError:
    print('delivercute superuser already in database.')

for subreddit_name in SUBREDDIT_NAMES:
    try:
        new = SubReddit(display_name=subreddit_name)
        new.save()
    except IntegrityError:
        print('SubReddit {} already in database.'.format(subreddit_name))

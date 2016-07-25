#!/usr/bin/python
"""Run commands upon deployment to set up admin user and initial subreddits."""

import os
import sys
import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "delivercute.settings")
django.setup()
from django.contrib.auth.models import User
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

superuser = User.objects.create_superuser('delivercute', EMAIL, PASSWORD)
superuser.save()

for subreddit_name in SUBREDDIT_NAMES:
    new = SubReddit(display_name=subreddit_name)
    new.save()

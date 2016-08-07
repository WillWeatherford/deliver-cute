"""Hold constant values used in multiple places in project."""
from __future__ import unicode_literals, absolute_import
import os

try:
    UNICODE = unicode
    print('Python 2, using unicode class.')
except NameError:
    UNICODE = str
    print('Python 3, using str class.')

HOME = '/'
SECRET_KEY = os.environ['PROJECT_EMAIL']
EMAIL = os.environ['PROJECT_EMAIL']
PASSWORD = os.environ['PROJECT_PASSWORD']
APP_PASSWORD = os.environ['PROJECT_APP_PASSWORD']

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
    'redpandas',
]

LIMIT = 10

SUCCESS_MSG = {
    'new': 'Thanks for subscribing to Deliver Cute!',
    'update': 'Subscription updated.',
}

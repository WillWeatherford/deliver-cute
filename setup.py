"""Setup for Deliver Cute project."""
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


setup(name='Deliver Cute',
      version='1.0',
      description='Send cute images from reddit to subscribers.',
      # long_description=README + '\n\n' + CHANGES,
      author=('Will Weatherford'),
      author_email='weatherford.william@gmail.com',
      url='http://delivercute.will-weatherford.com',
      license='MIT',
      keywords='django, praw',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='delivercute',
      )

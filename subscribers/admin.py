"""Register subscribers models to be available on admin page."""

from django.contrib import admin
from .models import Subscriber, SubReddit

admin.site.register(Subscriber)
admin.site.register(SubReddit)

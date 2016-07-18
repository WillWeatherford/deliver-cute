"""Register subscribers models to be available on admin page."""

from django.contrib import admin
from .models import Subscriber

admin.site.register(Subscriber)

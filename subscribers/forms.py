"""Subscriber Forms."""
from django import forms
from .models import Subscriber, SubReddit


class SubscriberForm(forms.ModelForm):
    """Customized ModelForm allowing using multiple select widget."""

    class Meta:
        """Establish model and fields for SubscriberForm."""

        model = Subscriber
        fields = ['email', 'send_hour', 'subreddits']

    subreddits = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=SubReddit.objects.order_by('display_name'),
        # initial=list(range(1, SubReddit.objects.count() + 1)),
    )

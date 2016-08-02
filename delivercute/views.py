"""Views for Deliver Cute website."""

from django.views.generic import CreateView, DeleteView
from django.http import HttpResponseRedirect
# from django.core.urlresolvers import reverse
from subscribers.models import Subscriber
from subscribers.forms import SubscriberForm


class Main(CreateView):
    """Main page input form to create or update subscriber information."""

    template_name = 'main.html'
    model = Subscriber
    form_class = SubscriberForm
    success_url = '/'

    def form_valid(self, form):
        """Create new Subscriber instance or update if already in database."""
        data = form.cleaned_data
        subreddits = data.pop('subreddits')
        instance, created = Subscriber.objects.update_or_create(
            email=data.get('email', ''),
            defaults=data,
        )
        instance.save()
        instance.subreddits.add(*subreddits)
        self.object = instance
        return HttpResponseRedirect(self.get_success_url())


class Unsubcribe(DeleteView):
    """Prompt user to confirm they want to unsubscribe."""

    success_url = '/'
    model = Subscriber

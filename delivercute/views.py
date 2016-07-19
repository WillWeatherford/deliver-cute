"""Views for Deliver Cute website."""

from subscribers.models import Subscriber
from subscribers.forms import SubscriberForm
from django.views.generic import CreateView
from django.http import HttpResponseRedirect


class Main(CreateView):
    """Main page input form to create or update subscriber information."""

    template_name = 'main.html'
    model = Subscriber
    form_class = SubscriberForm
    success_url = '/'

    def form_valid(self, form):
        """Create new Subscriber instance or update if already in database."""
        data = form.cleaned_data
        instance, created = Subscriber.objects.update_or_create(
            email=data.get('email', ''),
            defaults=data,
        )
        instance.save()
        self.object = instance
        return HttpResponseRedirect(self.get_success_url())

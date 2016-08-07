"""Views for Deliver Cute website."""

from django.views.generic import CreateView, DeleteView, TemplateView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from subscribers.models import Subscriber
from subscribers.forms import SubscriberForm
from constants import SUCCESS_MSG


class Main(CreateView):
    """Main page input form to create or update subscriber information."""

    template_name = 'main.html'
    model = Subscriber
    form_class = SubscriberForm

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
        url = reverse_lazy('success', kwargs={
            'status': 'new' * created or 'update'
        })
        return HttpResponseRedirect(url)


class Success(TemplateView):
    """Simple view giving success message after subscribe or update."""

    template_name = 'success.html'

    def get_context_data(self, *args, **kwargs):
        """Insert new or updated subscriber message into template."""
        data = super(Success, self).get_context_data(*args, **kwargs)
        data['message'] = SUCCESS_MSG[data['status']]
        return data


class Unsubcribe(DeleteView):
    """Prompt user to confirm they want to unsubscribe."""

    success_url = reverse_lazy('home')
    model = Subscriber
    slug_field = 'unsubscribe_hash'

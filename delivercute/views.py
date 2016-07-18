from subscribers.models import Subscriber
from django.views.generic import CreateView
from django.http import HttpResponseRedirect


class Main(CreateView):
    template_name = 'main.html'
    model = Subscriber
    fields = ['email', 'send_hour']
    success_url = '/'

    def form_valid(self, form):
        data = form.cleaned_data
        instance, created = Subscriber.objects.update_or_create(
            email=data.get('email', ''),
            defaults=data,
        )
        instance.save()
        self.object = instance
        return HttpResponseRedirect(self.get_success_url())

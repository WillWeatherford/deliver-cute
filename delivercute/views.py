from django.views.generic import CreateView
from subscribers.models import Subscriber


class Main(CreateView):
    template_name = 'main.html'
    model = Subscriber
    fields = ['email', 'send_hour']
    success_url = '/'

    def form_valid(self, form):
        # utilizing form_valid of ModelFormMixin

        data = form.cleaned_data
        instance, created = Subscriber.objects.update_or_create(
            email=data.get('email', ''),
            defaults=data)
        import pdb;pdb.set_trace()
        instance.save()
        self.object = instance
        return super(CreateView, self).form_valid(form)

from django.views.generic import CreateView
from subscribers.models import Subscriber


class Main(CreateView):
    template_name = 'main.html'
    model = Subscriber
    fields = ['email', 'send_hour']
    success_url = '/'


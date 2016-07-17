from django.views.generic import CreateView
from subscribers.models import Subscriber


class Main(CreateView):
    template_name = 'main.html'
    model = Subscriber
    fields = ['email', 'send_hour']
    # load a form - CreateView?
    # save or update preferences
    # modelview

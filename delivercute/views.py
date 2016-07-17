from django.views.generic import TemplateView

class Main(TemplateView):
    template_name = 'main.html'
    # load a form - CreateView?
    # save or update preferences
    # modelview

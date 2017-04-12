from django.apps import AppConfig


class SubscribersConfig(AppConfig):
    name = 'subscribers'

    def ready(self):
        from subscribers import handlers

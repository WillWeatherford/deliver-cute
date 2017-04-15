from django.db.models import signals
from django.dispatch import receiver
from subscribers.models import Subscriber, SubReddit

# We want to log for any Subscriber the changes in their subreddits


@receiver(signals.m2m_changed, sender=Subscriber.subreddits.through)
def log_subscriber_changes(sender, instance=None, pk_set=(), action=None, **kwargs):
    print(action)
    if isinstance(instance, Subscriber):
        changed_subreddits = set(SubReddit.objects.filter(pk__in=pk_set))
        instance.log_subreddits_before_change(changed_subreddits, action)
    elif isinstance(instance, SubReddit):
        for subscriber in instance.subscribers.filter(pk__in=pk_set):
            subscriber.log_subreddits_before_change({instance, }, action)

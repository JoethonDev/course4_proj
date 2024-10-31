from django.core.signals import request_finished
from django.db.models.signals import post_save
from django.dispatch import receiver

from movies.models import SearchTerm
from movies.tasks import notify_of_new_search_term

@receiver(request_finished)
def signal_receiver(sender, **kwargs):
  print(f"Received signal from {sender}")


@receiver(post_save, sender=SearchTerm, dispatch_uid="search_term_save")
def search_term_saved(sender, instance, created, **kwargs):
    if created:
      notify_of_new_search_term.delay(instance.term)
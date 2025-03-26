from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ExampleState

@receiver(post_save, sender=ExampleState)
def check_for_disagreements(sender, instance, created, **kwargs):
    if created:
        # Check for disagreements whenever a new state is created
        instance.example.states.check_for_disagreements(instance.example)
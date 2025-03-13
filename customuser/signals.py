from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User, Group


@receiver(m2m_changed, sender=User.groups.through)
def update_is_staff(sender, instance, action, **kwargs):

    if action in ["post_add", "post_remove", "post_clear"]:
        staff_groups = [
            "Customer",
            "Factory Manager",
            "Store Manager",
        ]

        if instance.groups.filter(name__in=staff_groups).exists():
            instance.is_staff = True
        else:
            instance.is_staff = False

        instance.save()

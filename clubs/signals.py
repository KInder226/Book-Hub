from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from notifications.signals import notify
from .models import Club, ClubMembership

User = get_user_model()


@receiver(post_save, sender=ClubMembership)
def notify_new_member(sender, instance, created, **kwargs):
    """Отправляет уведомление о новом участнике клуба"""
    if created:
        # Уведомляем администраторов и модераторов клуба
        admins_and_mods = ClubMembership.objects.filter(
            club=instance.club,
            role__in=['admin', 'moderator']
        ).exclude(user=instance.user)
        
        for membership in admins_and_mods:
            notify.send(
                instance.user,
                recipient=membership.user,
                verb='присоединился к клубу',
                action_object=instance,
                target=instance.club,
                description=f'{instance.user.username} присоединился к клубу "{instance.club.name}"'
            )


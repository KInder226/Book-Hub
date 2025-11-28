from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ReadingProgress


@receiver(post_save, sender=ReadingProgress)
def update_user_statistics(sender, instance, **kwargs):
    """Обновляет статистику пользователя при изменении прогресса чтения"""
    instance.user.profile.update_statistics()


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from notifications.signals import notify
from .models import Post, Comment

User = get_user_model()


@receiver(post_save, sender=Post)
def notify_new_post(sender, instance, created, **kwargs):
    """Отправляет уведомление участникам клуба о новом посте"""
    if created:
        # Уведомляем всех участников клуба, кроме автора
        members = instance.club.members.exclude(pk=instance.author.pk)
        for member in members:
            notify.send(
                instance.author,
                recipient=member,
                verb='создал новый пост',
                action_object=instance,
                target=instance.club,
                description=f'Новый пост в клубе "{instance.club.name}": {instance.title}'
            )


@receiver(post_save, sender=Comment)
def notify_new_comment(sender, instance, created, **kwargs):
    """Отправляет уведомление автору поста о новом комментарии"""
    if created:
        # Уведомляем автора поста, если это не его комментарий
        if instance.post.author != instance.author:
            notify.send(
                instance.author,
                recipient=instance.post.author,
                verb='оставил комментарий',
                action_object=instance,
                target=instance.post,
                description=f'Новый комментарий к посту "{instance.post.title}"'
            )
        
        # Уведомляем автора родительского комментария, если есть ответ
        if instance.parent and instance.parent.author != instance.author:
            notify.send(
                instance.author,
                recipient=instance.parent.author,
                verb='ответил на ваш комментарий',
                action_object=instance,
                target=instance.post,
                description=f'Ответ на ваш комментарий к посту "{instance.post.title}"'
            )


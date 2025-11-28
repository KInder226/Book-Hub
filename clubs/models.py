from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

User = get_user_model()


class Club(models.Model):
    """Книжный клуб"""
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('moderator', 'Модератор'),
        ('member', 'Участник'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    cover = models.ImageField(upload_to='club_covers/', blank=True, null=True, verbose_name='Обложка')
    is_private = models.BooleanField(default=False, verbose_name='Приватный')
    invitation_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name='Код приглашения')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_clubs', verbose_name='Создатель')
    current_book = models.ForeignKey('books.Book', on_delete=models.SET_NULL, blank=True, null=True, related_name='active_clubs', verbose_name='Текущая книга')
    reading_start_date = models.DateField(blank=True, null=True, verbose_name='Начало чтения')
    reading_end_date = models.DateField(blank=True, null=True, verbose_name='Конец чтения')
    members = models.ManyToManyField(User, through='ClubMembership', related_name='clubs', verbose_name='Участники')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = _('Клуб')
        verbose_name_plural = _('Клубы')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('clubs:detail', kwargs={'pk': self.pk})
    
    def get_invitation_link(self):
        """Возвращает ссылку для приглашения"""
        return reverse('clubs:join', kwargs={'invitation_code': self.invitation_code})
    
    def is_member(self, user):
        """Проверяет, является ли пользователь участником"""
        if not user.is_authenticated:
            return False
        return ClubMembership.objects.filter(club=self, user=user).exists()
    
    def get_user_role(self, user):
        """Возвращает роль пользователя в клубе"""
        if not self.is_member(user):
            return None
        membership = ClubMembership.objects.get(club=self, user=user)
        return membership.role
    
    def can_manage(self, user):
        """Проверяет, может ли пользователь управлять клубом"""
        role = self.get_user_role(user)
        return role in ['admin', 'moderator']


class ClubMembership(models.Model):
    """Членство в клубе с ролями"""
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('moderator', 'Модератор'),
        ('member', 'Участник'),
    ]
    
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='memberships', verbose_name='Клуб')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='club_memberships', verbose_name='Пользователь')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', verbose_name='Роль')
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата присоединения')
    
    class Meta:
        verbose_name = _('Членство в клубе')
        verbose_name_plural = _('Членства в клубах')
        unique_together = ['club', 'user']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.club.name} ({self.get_role_display()})'


class ClubInvitation(models.Model):
    """Приглашение в клуб"""
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='invitations', verbose_name='Клуб')
    email = models.EmailField(verbose_name='Email')
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations', verbose_name='Пригласил')
    is_accepted = models.BooleanField(default=False, verbose_name='Принято')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    accepted_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата принятия')
    
    class Meta:
        verbose_name = _('Приглашение')
        verbose_name_plural = _('Приглашения')
        unique_together = ['club', 'email']
        ordering = ['-created_at']
    
    def __str__(self):
        status = 'Принято' if self.is_accepted else 'Ожидает'
        return f'{self.email} - {self.club.name} ({status})'


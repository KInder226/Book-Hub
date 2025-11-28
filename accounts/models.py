from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Расширенная модель пользователя"""
    email = models.EmailField(_('email address'), unique=True)
    
    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
    
    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """Профиль пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    bio = models.TextField(max_length=500, blank=True, verbose_name='О себе')
    favorite_genres = models.ManyToManyField('books.Genre', blank=True, verbose_name='Любимые жанры')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    # Статистика
    books_read = models.IntegerField(default=0, verbose_name='Прочитано книг')
    clubs_count = models.IntegerField(default=0, verbose_name='Количество клубов')
    
    class Meta:
        verbose_name = _('Профиль пользователя')
        verbose_name_plural = _('Профили пользователей')
    
    def __str__(self):
        return f'Профиль {self.user.username}'
    
    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'username': self.user.username})
    
    def update_statistics(self):
        """Обновляет статистику пользователя"""
        from clubs.models import ClubMembership
        from books.models import ReadingProgress
        
        self.clubs_count = ClubMembership.objects.filter(user=self.user).count()
        self.books_read = ReadingProgress.objects.filter(
            user=self.user,
            is_completed=True
        ).count()
        self.save()


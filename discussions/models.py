from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

User = get_user_model()


class PostTag(models.Model):
    """Теги для постов"""
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='URL')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Цвет')
    
    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Post(models.Model):
    """Пост в обсуждении клуба"""
    POST_TYPE_CHOICES = [
        ('discussion', 'Обсуждение'),
        ('question', 'Вопрос'),
        ('quote', 'Цитата'),
        ('note', 'Заметка'),
    ]
    
    club = models.ForeignKey('clubs.Club', on_delete=models.CASCADE, related_name='posts', verbose_name='Клуб')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name='Автор')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, default='discussion', verbose_name='Тип поста')
    chapter = models.IntegerField(blank=True, null=True, verbose_name='Глава')
    tags = models.ManyToManyField(PostTag, blank=True, related_name='posts', verbose_name='Теги')
    is_pinned = models.BooleanField(default=False, verbose_name='Закреплен')
    is_locked = models.BooleanField(default=False, verbose_name='Закрыт')
    likes = models.ManyToManyField(User, blank=True, related_name='liked_posts', verbose_name='Лайки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = _('Пост')
        verbose_name_plural = _('Посты')
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['club', '-created_at']),
        ]
    
    def __str__(self):
        return f'{self.title} - {self.club.name}'
    
    def get_absolute_url(self):
        return reverse('discussions:post_detail', kwargs={'pk': self.pk})
    
    @property
    def likes_count(self):
        return self.likes.count()
    
    @property
    def comments_count(self):
        return self.comments.count()


class Comment(MPTTModel):
    """Комментарий к посту (с поддержкой иерархии)"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='Пост')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='Автор')
    content = models.TextField(verbose_name='Содержание')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name='Родительский комментарий')
    likes = models.ManyToManyField(User, blank=True, related_name='liked_comments', verbose_name='Лайки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class MPTTMeta:
        order_insertion_by = ['created_at']
    
    class Meta:
        verbose_name = _('Комментарий')
        verbose_name_plural = _('Комментарии')
        ordering = ['tree_id', 'lft']
    
    def __str__(self):
        return f'Комментарий от {self.author.username} к посту "{self.post.title}"'
    
    @property
    def likes_count(self):
        return self.likes.count()


class PostReport(models.Model):
    """Жалоба на пост"""
    REPORT_REASON_CHOICES = [
        ('spam', 'Спам'),
        ('inappropriate', 'Неподходящий контент'),
        ('harassment', 'Домогательство'),
        ('other', 'Другое'),
    ]
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports', verbose_name='Пост')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_reports', verbose_name='Жалобщик')
    reason = models.CharField(max_length=20, choices=REPORT_REASON_CHOICES, verbose_name='Причина')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_resolved = models.BooleanField(default=False, verbose_name='Решено')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = _('Жалоба на пост')
        verbose_name_plural = _('Жалобы на посты')
        unique_together = ['post', 'reporter']
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Жалоба на пост "{self.post.title}" от {self.reporter.username}'


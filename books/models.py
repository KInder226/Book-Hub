from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Genre(models.Model):
    """Жанр книги"""
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Описание')
    
    class Meta:
        verbose_name = _('Жанр')
        verbose_name_plural = _('Жанры')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Book(models.Model):
    """Книга"""
    title = models.CharField(max_length=200, verbose_name='Название')
    author = models.CharField(max_length=200, verbose_name='Автор')
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name='ISBN')
    description = models.TextField(verbose_name='Описание')
    cover = models.ImageField(upload_to='book_covers/', blank=True, null=True, verbose_name='Обложка')
    genres = models.ManyToManyField(Genre, related_name='books', verbose_name='Жанры')
    pages = models.IntegerField(default=0, verbose_name='Количество страниц')
    published_year = models.IntegerField(blank=True, null=True, verbose_name='Год издания')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = _('Книга')
        verbose_name_plural = _('Книги')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title', 'author']),
        ]
    
    def __str__(self):
        return f'{self.title} - {self.author}'
    
    def get_absolute_url(self):
        return reverse('books:detail', kwargs={'pk': self.pk})


class ReadingProgress(models.Model):
    """Прогресс чтения пользователя"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_progresses', verbose_name='Пользователь')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reading_progresses', verbose_name='Книга')
    current_chapter = models.IntegerField(default=1, verbose_name='Текущая глава')
    pages_read = models.IntegerField(default=0, verbose_name='Прочитано страниц')
    is_completed = models.BooleanField(default=False, verbose_name='Прочитана')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Начало чтения')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='Завершено')
    notes = models.TextField(blank=True, verbose_name='Заметки')
    
    class Meta:
        verbose_name = _('Прогресс чтения')
        verbose_name_plural = _('Прогрессы чтения')
        unique_together = ['user', 'book']
        ordering = ['-started_at']
    
    def __str__(self):
        status = 'Завершено' if self.is_completed else 'В процессе'
        return f'{self.user.username} - {self.book.title} ({status})'
    
    def save(self, *args, **kwargs):
        if self.is_completed and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()
            if self.book.pages > 0:
                self.pages_read = self.book.pages
        
        super().save(*args, **kwargs)
        
        # Обновляем статистику пользователя
        self.user.profile.update_statistics()
    
    @property
    def progress_percentage(self):
        """Процент прочитанного"""
        if self.book.pages > 0:
            return min(100, int((self.pages_read / self.book.pages) * 100))
        return 0


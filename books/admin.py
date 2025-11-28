from django.contrib import admin
from .models import Genre, Book, ReadingProgress


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_year', 'created_at')
    list_filter = ('genres', 'published_year', 'created_at')
    search_fields = ('title', 'author', 'isbn')
    filter_horizontal = ('genres',)
    prepopulated_fields = {}
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'current_chapter', 'pages_read', 'is_completed', 'started_at')
    list_filter = ('is_completed', 'started_at')
    search_fields = ('user__username', 'book__title')
    readonly_fields = ('started_at', 'completed_at')


from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import PostTag, Post, Comment, PostReport


@admin.register(PostTag)
class PostTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'club', 'author', 'post_type', 'is_pinned', 'is_locked', 'created_at')
    list_filter = ('post_type', 'is_pinned', 'is_locked', 'created_at', 'club')
    search_fields = ('title', 'content', 'author__username', 'club__name')
    filter_horizontal = ('tags', 'likes')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(MPTTModelAdmin):
    list_display = ('author', 'post', 'content_preview', 'likes_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'post__title')
    mptt_level_indent = 20
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Содержание'
    
    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Лайков'


@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    list_display = ('post', 'reporter', 'reason', 'is_resolved', 'created_at')
    list_filter = ('reason', 'is_resolved', 'created_at')
    search_fields = ('post__title', 'reporter__username', 'description')
    readonly_fields = ('created_at',)
    list_editable = ('is_resolved',)


"""
URL configuration for bookclubhub project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('clubs.urls')),
    path('accounts/', include('accounts.urls')),
    path('books/', include('books.urls')),
    path('discussions/', include('discussions.urls')),
    path('notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]

# Jazzmin настроен в settings.py, поэтому эти строки не нужны
# admin.site.site_header = 'BookClub Hub - Админ-панель'
# admin.site.site_title = 'BookClub Hub'
# admin.site.index_title = 'Управление платформой'


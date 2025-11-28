from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.BookListView.as_view(), name='list'),
    path('<int:pk>/', views.BookDetailView.as_view(), name='detail'),
    path('add/', views.add_book, name='add'),
    path('<int:book_id>/progress/', views.update_reading_progress, name='update_progress'),
]


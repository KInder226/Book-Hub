from django.urls import path
from . import views

app_name = 'discussions'

urlpatterns = [
    path('club/<int:club_id>/', views.PostListView.as_view(), name='club_posts'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('club/<int:club_id>/create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/like/', views.toggle_like_post, name='toggle_like'),
    path('post/<int:post_id>/report/', views.report_post, name='report_post'),
]


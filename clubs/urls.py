from django.urls import path
from . import views

app_name = 'clubs'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('clubs/', views.ClubListView.as_view(), name='list'),
    path('clubs/<int:pk>/', views.ClubDetailView.as_view(), name='detail'),
    path('clubs/create/', views.create_club, name='create'),
    path('clubs/join/<uuid:invitation_code>/', views.join_club, name='join'),
    path('clubs/<int:club_id>/leave/', views.leave_club, name='leave'),
    path('clubs/<int:club_id>/invite/', views.invite_member, name='invite'),
    path('clubs/<int:club_id>/set-book/', views.set_current_book, name='set_book'),
]


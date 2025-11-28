from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.urls import reverse_lazy
from .models import Club, ClubMembership, ClubInvitation
from .forms import ClubForm, ClubInvitationForm
from books.models import Book, ReadingProgress


class HomeView(TemplateView):
    """Главная страница"""
    template_name = 'clubs/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Статистика для главной страницы
        context['total_clubs'] = Club.objects.filter(is_private=False).count()
        context['total_books'] = Book.objects.count()
        context['recent_clubs'] = Club.objects.filter(is_private=False).order_by('-created_at')[:6]
        if self.request.user.is_authenticated:
            context['user_clubs'] = Club.objects.filter(members=self.request.user)[:5]
        return context


class ClubListView(ListView):
    """Список всех клубов"""
    model = Club
    template_name = 'clubs/list.html'
    context_object_name = 'clubs'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Club.objects.select_related('created_by', 'current_book').prefetch_related('members')
        search_query = self.request.GET.get('search', '')
        is_private = self.request.GET.get('is_private', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        if is_private == 'public':
            queryset = queryset.filter(is_private=False)
        elif is_private == 'private':
            queryset = queryset.filter(is_private=True)
        
        # Для неавторизованных пользователей показываем только публичные
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_private=False)
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_privacy'] = self.request.GET.get('is_private', '')
        if self.request.user.is_authenticated:
            context['user_clubs'] = Club.objects.filter(members=self.request.user)
        return context


class ClubDetailView(DetailView):
    """Детальная страница клуба"""
    model = Club
    template_name = 'clubs/detail.html'
    context_object_name = 'club'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_authenticated:
            context['is_member'] = self.object.is_member(user)
            context['user_role'] = self.object.get_user_role(user)
            context['memberships'] = ClubMembership.objects.filter(club=self.object).select_related('user')
            
            # Прогресс чтения текущей книги
            if self.object.current_book:
                context['user_progress'] = ReadingProgress.objects.filter(
                    user=user,
                    book=self.object.current_book
                ).first()
        else:
            context['is_member'] = False
            context['user_role'] = None
        
        return context


@login_required
def create_club(request):
    """Создание нового клуба"""
    if request.method == 'POST':
        form = ClubForm(request.POST, request.FILES)
        if form.is_valid():
            club = form.save(commit=False)
            club.created_by = request.user
            club.save()
            form.save_m2m()
            
            # Автоматически добавляем создателя как администратора
            ClubMembership.objects.create(
                club=club,
                user=request.user,
                role='admin'
            )
            
            messages.success(request, f'Клуб "{club.name}" успешно создан!')
            return redirect('clubs:detail', pk=club.pk)
    else:
        form = ClubForm()
    return render(request, 'clubs/create.html', {'form': form})


@login_required
def join_club(request, invitation_code):
    """Присоединение к клубу по коду приглашения"""
    try:
        club = Club.objects.get(invitation_code=invitation_code)
    except Club.DoesNotExist:
        messages.error(request, 'Клуб не найден.')
        return redirect('clubs:list')
    
    if club.is_member(request.user):
        messages.info(request, 'Вы уже являетесь участником этого клуба.')
        return redirect('clubs:detail', pk=club.pk)
    
    if request.method == 'POST':
        ClubMembership.objects.create(
            club=club,
            user=request.user,
            role='member'
        )
        messages.success(request, f'Вы успешно присоединились к клубу "{club.name}"!')
        return redirect('clubs:detail', pk=club.pk)
    
    return render(request, 'clubs/join.html', {'club': club})


@login_required
def leave_club(request, club_id):
    """Выход из клуба"""
    club = get_object_or_404(Club, pk=club_id)
    
    if not club.is_member(request.user):
        messages.error(request, 'Вы не являетесь участником этого клуба.')
        return redirect('clubs:list')
    
    user_role = club.get_user_role(request.user)
    
    # Администратор не может покинуть клуб, если он единственный
    if user_role == 'admin':
        admin_count = ClubMembership.objects.filter(club=club, role='admin').count()
        if admin_count == 1:
            messages.error(request, 'Вы не можете покинуть клуб, так как являетесь единственным администратором.')
            return redirect('clubs:detail', pk=club.pk)
    
    if request.method == 'POST':
        ClubMembership.objects.filter(club=club, user=request.user).delete()
        messages.success(request, f'Вы покинули клуб "{club.name}".')
        return redirect('clubs:list')
    
    return render(request, 'clubs/leave.html', {'club': club})


@login_required
def invite_member(request, club_id):
    """Приглашение нового участника"""
    club = get_object_or_404(Club, pk=club_id)
    
    if not club.can_manage(request.user):
        messages.error(request, 'У вас нет прав для приглашения участников.')
        return redirect('clubs:detail', pk=club.pk)
    
    if request.method == 'POST':
        form = ClubInvitationForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.club = club
            invitation.invited_by = request.user
            invitation.save()
            
            # TODO: Отправить email с приглашением
            messages.success(request, f'Приглашение отправлено на {invitation.email}!')
            return redirect('clubs:detail', pk=club.pk)
    else:
        form = ClubInvitationForm()
    
    return render(request, 'clubs/invite.html', {'form': form, 'club': club})


@login_required
def set_current_book(request, club_id):
    """Установка текущей книги для клуба"""
    club = get_object_or_404(Club, pk=club_id)
    
    if not club.can_manage(request.user):
        messages.error(request, 'У вас нет прав для изменения текущей книги.')
        return redirect('clubs:detail', pk=club.pk)
    
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        start_date = request.POST.get('reading_start_date')
        end_date = request.POST.get('reading_end_date')
        
        if book_id:
            book = get_object_or_404(Book, pk=book_id)
            club.current_book = book
            if start_date:
                club.reading_start_date = start_date
            if end_date:
                club.reading_end_date = end_date
            club.save()
            messages.success(request, f'Текущая книга установлена: "{book.title}"')
        else:
            club.current_book = None
            club.save()
            messages.success(request, 'Текущая книга удалена.')
        
        return redirect('clubs:detail', pk=club.pk)
    
    books = Book.objects.all().order_by('title')
    return render(request, 'clubs/set_book.html', {'club': club, 'books': books})


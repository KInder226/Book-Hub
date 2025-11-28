from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Q
from .models import Post, Comment, PostTag, PostReport
from .forms import PostForm, CommentForm, PostReportForm
from clubs.models import Club


class PostListView(ListView):
    """Список постов клуба"""
    model = Post
    template_name = 'discussions/post_list.html'
    context_object_name = 'posts'
    paginate_by = 20
    
    def get_queryset(self):
        club_id = self.kwargs.get('club_id')
        club = get_object_or_404(Club, pk=club_id)
        
        queryset = Post.objects.filter(club=club).select_related('author', 'club').prefetch_related('tags', 'likes')
        
        # Фильтры
        post_type = self.request.GET.get('type', '')
        tag_slug = self.request.GET.get('tag', '')
        search_query = self.request.GET.get('search', '')
        
        if post_type:
            queryset = queryset.filter(post_type=post_type)
        
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        club_id = self.kwargs.get('club_id')
        club = get_object_or_404(Club, pk=club_id)
        context['club'] = club
        context['tags'] = PostTag.objects.all()
        context['post_types'] = Post.POST_TYPE_CHOICES
        context['selected_type'] = self.request.GET.get('type', '')
        context['selected_tag'] = self.request.GET.get('tag', '')
        context['search_query'] = self.request.GET.get('search', '')
        
        # Проверка прав
        if self.request.user.is_authenticated:
            context['can_create'] = club.is_member(self.request.user)
            context['can_moderate'] = club.can_manage(self.request.user)
        else:
            context['can_create'] = False
            context['can_moderate'] = False
        
        return context


class PostDetailView(DetailView):
    """Детальная страница поста"""
    model = Post
    template_name = 'discussions/post_detail.html'
    context_object_name = 'post'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(post=self.object).select_related('author')
        context['comment_form'] = CommentForm()
        
        if self.request.user.is_authenticated:
            context['is_liked'] = self.object.likes.filter(pk=self.request.user.pk).exists()
            context['can_moderate'] = self.object.club.can_manage(self.request.user)
        else:
            context['is_liked'] = False
            context['can_moderate'] = False
        
        return context


@login_required
def create_post(request, club_id):
    """Создание нового поста"""
    club = get_object_or_404(Club, pk=club_id)
    
    if not club.is_member(request.user):
        messages.error(request, 'Вы должны быть участником клуба, чтобы создавать посты.')
        return redirect('clubs:detail', pk=club_id)
    
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.club = club
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, 'Пост успешно создан!')
            return redirect('discussions:post_detail', pk=post.pk)
    else:
        form = PostForm()
    
    return render(request, 'discussions/create_post.html', {'form': form, 'club': club})


@login_required
def add_comment(request, post_id):
    """Добавление комментария к посту"""
    post = get_object_or_404(Post, pk=post_id)
    
    if post.is_locked:
        messages.error(request, 'Обсуждение закрыто для комментариев.')
        return redirect('discussions:post_detail', pk=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен!')
            return redirect('discussions:post_detail', pk=post_id)
    else:
        form = CommentForm()
    
    return render(request, 'discussions/add_comment.html', {'form': form, 'post': post})


@login_required
def toggle_like_post(request, post_id):
    """Лайк/дизлайк поста"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    post = get_object_or_404(Post, pk=post_id)
    
    if post.likes.filter(pk=request.user.pk).exists():
        post.likes.remove(request.user)
        is_liked = False
    else:
        post.likes.add(request.user)
        is_liked = True
    
    return JsonResponse({
        'is_liked': is_liked,
        'likes_count': post.likes.count()
    })


@login_required
def report_post(request, post_id):
    """Жалоба на пост"""
    post = get_object_or_404(Post, pk=post_id)
    
    if PostReport.objects.filter(post=post, reporter=request.user).exists():
        messages.error(request, 'Вы уже отправили жалобу на этот пост.')
        return redirect('discussions:post_detail', pk=post_id)
    
    if request.method == 'POST':
        form = PostReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.post = post
            report.reporter = request.user
            report.save()
            messages.success(request, 'Жалоба отправлена. Модераторы рассмотрят её в ближайшее время.')
            return redirect('discussions:post_detail', pk=post_id)
    else:
        form = PostReportForm()
    
    return render(request, 'discussions/report_post.html', {'form': form, 'post': post})


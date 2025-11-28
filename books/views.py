from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Book, Genre, ReadingProgress
from .forms import BookForm, ReadingProgressForm


class BookListView(ListView):
    """Список всех книг"""
    model = Book
    template_name = 'books/list.html'
    context_object_name = 'books'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Book.objects.select_related().prefetch_related('genres')
        search_query = self.request.GET.get('search', '')
        genre_slug = self.request.GET.get('genre', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(isbn__icontains=search_query)
            )
        
        if genre_slug:
            queryset = queryset.filter(genres__slug=genre_slug)
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_genre'] = self.request.GET.get('genre', '')
        return context


class BookDetailView(DetailView):
    """Детальная страница книги"""
    model = Book
    template_name = 'books/detail.html'
    context_object_name = 'book'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_progress'] = ReadingProgress.objects.filter(
                user=self.request.user,
                book=self.object
            ).first()
        return context


@login_required
def add_book(request):
    """Добавление новой книги"""
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Книга "{book.title}" успешно добавлена!')
            return redirect('books:detail', pk=book.pk)
    else:
        form = BookForm()
    return render(request, 'books/add.html', {'form': form})


@login_required
def update_reading_progress(request, book_id):
    """Обновление прогресса чтения"""
    book = get_object_or_404(Book, pk=book_id)
    progress, created = ReadingProgress.objects.get_or_create(
        user=request.user,
        book=book
    )
    
    if request.method == 'POST':
        form = ReadingProgressForm(request.POST, instance=progress)
        if form.is_valid():
            form.save()
            messages.success(request, 'Прогресс обновлен!')
            return redirect('books:detail', pk=book.pk)
    else:
        form = ReadingProgressForm(instance=progress)
    
    return render(request, 'books/update_progress.html', {
        'form': form,
        'book': book,
        'progress': progress,
    })


from django.shortcuts import render, get_object_or_404, Http404
from .models import Book, Chapter, Exercise
from shopping_cart.models import Order,OrderItem

# Create your views here.


def book_list(request):
    queryset = Book.objects.all()
    context = {
        'queryset': queryset
    }
    return render(request, 'book_list.html', context)


def book_detail(request, slug):
    book = get_object_or_404(Book, slug=slug)
    order = Order.objects.get(user=request.user)
    order_item=OrderItem.objects.get(book=book)
    book_is_in_cart=False
    if order_item in order.items.all():
        book_is_in_cart=True
    context = {
        'book': book,
        'in_cart':book_is_in_cart
    }
    return render(request, 'book_detail.html', context)


def chapter_detail(request, book_slug, chapter_number):
    chapter_qs = Chapter.objects\
        .filter(book__slug=book_slug)\
        .filter(chapter_number=chapter_number)
    if chapter_qs.exists():
        context = {
            'chapter': chapter_qs[0]
        }
        return render(request, 'chapter_detail.html', context)
    raise Http404


def exercise_detail(request, book_slug, chapter_number, exercise_number):
    exercise_qs = Exercise.objects\
        .filter(chapter__book__slug=book_slug)\
        .filter(chapter__chapter_number=chapter_number)\
        .filter(exercise_number=exercise_number)
    if exercise_qs.exists():
        context = {
            'exercise': exercise_qs[0]
        }
        return render(request, 'exercise_detail.html', context)
    raise Http404

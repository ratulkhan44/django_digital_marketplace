from django.shortcuts import render
from .models import Book

# Create your views here.

def book_list(request):
    queryset=Book.objects.all()
    context={
        'queryset':queryset
    }
    return render(request,'book_list.html',context)

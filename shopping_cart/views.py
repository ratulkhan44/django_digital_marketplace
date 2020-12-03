from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from books.models import Book
from .models import Order, OrderItem, Payment
from django.conf import settings
import stripe
import random
import string

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.


def create_ref_code():
    return ''.join(random.choices(string.ascii_uppercase+string.digits, k=15))


def add_to_cart(request, book_slug):
    book = get_object_or_404(Book, slug=book_slug)
    order_item, created = OrderItem.objects.get_or_create(book=book)
    order, created = Order.objects.get_or_create(user=request.user)
    order.items.add(order_item)
    order.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def remove_from_cart(request, book_slug):
    book = get_object_or_404(Book, slug=book_slug)
    order_item = OrderItem.objects.get(book=book)
    order = Order.objects.get(user=request.user)
    order.items.remove(order_item)
    order.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def order_view(request):
    order = get_object_or_404(Order, user=request.user)
    context = {
        'order': order
    }
    return render(request, 'order_summary.html', context)


def checkout(request):
    order = get_object_or_404(Order, user=request.user)
    if request.method == 'POST':
        # complete the order (ref code and set the order true)
        order.ref_code = create_ref_code()
        token = request.POST.get('stripeToken')

        # create stripe charge

        charge = stripe.Charge.create(
            amount=order.get_total()*100,  # cents
            currency="usd",
            source=token,
            description=f"Charge for {request.user.username}",
        )

        print(charge)

        # # create our payment object and link to the order
        # payment = Payment()
        # payment.order = order
        # payment.stripe_charge_id = charge.id
        # payment.amount = order.get_total()
        # payment.save()

        # # add the book to the user book list
        # books = [item.book for item in order.items.all()]
        # for book in books:
        #     request.user.userlibrary.items.add(book)

        # redirect to user profile
        return redirect('/account/profile/')
    context = {
        'order': order
    }
    return render(request, 'checkout.html', context)

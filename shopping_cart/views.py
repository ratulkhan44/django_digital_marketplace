from django.http import HttpResponseRedirect, Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
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


@login_required
def add_to_cart(request, book_slug):
    book = get_object_or_404(Book, slug=book_slug)
    order_item, created = OrderItem.objects.get_or_create(book=book)
    order, created = Order.objects.get_or_create(
        user=request.user, is_ordered=False)
    order.items.add(order_item)
    order.save()
    messages.success(request, "Item successfully added to your cart")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
def remove_from_cart(request, book_slug):
    book = get_object_or_404(Book, slug=book_slug)
    order_item = OrderItem.objects.get(book=book)
    order = Order.objects.get(user=request.user, is_ordered=False)
    order.items.remove(order_item)
    order.save()
    messages.info(request, "Item successfully removed to your cart")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
def order_view(request):
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
    context = {
        'order': order
    }
    return render(request, 'order_summary.html', context)


@login_required
def checkout(request):
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
    else:
        raise Http404
    if request.method == 'POST':
        # complete the order (ref code and set the order true)
        try:
            order.ref_code = create_ref_code()

            # create stripe charge
            token = request.POST.get('stripeToken')
            charge = stripe.Charge.create(
                amount=int(order.get_total()*100),  # cents
                currency="usd",
                source=token,
                description=f"Charge for {request.user.username}",
            )

            # create our payment object and link to the order
            payment = Payment()
            payment.order = order
            payment.stripe_charge_id = charge.id
            payment.total_amount = order.get_total()
            payment.save()

            # add the book to the user book list
            books = [item.book for item in order.items.all()]
            for book in books:
                request.user.userlibrary.books.add(book)

            order.is_ordered = True
            order.save()
            messages.success(request, 'Your order Was Succesfull.')
            # redirect to user profile
            return redirect('/account/profile/')
        except stripe.error.CardError as e:
            messages.error(request, 'There Was a card error.')
            return redirect('cart:checkout')
        except stripe.error.RateLimitError as e:
            messages.error(request, 'There Was a Ratelimit error on stripe.')
            return redirect('cart:checkout')
        except stripe.error.InvalidRequestError as e:
            messages.error(request, 'Invalid parameters for Strope requests.')
            return redirect('cart:checkout')
        except stripe.error.AuthenticationError as e:
            messages.error(request, 'Invalid Stripe API keys')
            return redirect('cart:checkout')
        except stripe.error.APIConnectionError as e:
            messages.error(
                request, 'There Was a network error.Please try again')
            return redirect('cart:checkout')
        except stripe.error.StripeError as e:
            messages.error(request, 'There Was an error.Please try again')
            return redirect('cart:checkout')
        except Exception as e:
            messages.error(
                request, 'There Was a serious error.We are trying to resolve this.')
            return redirect('cart:checkout')

    context = {
        'order': order
    }
    return render(request, 'checkout.html', context)

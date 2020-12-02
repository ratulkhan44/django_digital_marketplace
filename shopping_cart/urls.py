from django.urls import path
from .views import add_to_cart, remove_from_cart, order_view

app_name = 'shopping_cart'

urlpatterns = [
    path('add-to-cart/<slug:book_slug>', add_to_cart, name="add_to_cart"),
    path('remove-from-cart/<slug:book_slug>',
         remove_from_cart, name="remove_from_cart"),
    path('order-summary/', order_view, name='order_summary')
]

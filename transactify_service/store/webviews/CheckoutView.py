from django.shortcuts import render
from django.views import View

from store.webmodels.StoreProduct import StoreProduct
from store.webmodels.Customer import Customer


class CheckoutView(View):
    template_name = 'store/checkout.html'
    def get(self, request, card_number=None, *args, **kwargs):
        # # Get the cart
        # cart = Cart.objects.get(user=request.user)

        # # Get the cart items
        # cart_items = CartItem.objects.filter(cart=cart)

        # # Get the total price of the cart
        # total_price = sum([item.product.price * item.quantity for item in cart_items])
        products = StoreProduct.objects.all()
        customer = Customer.objects.get(card_number=card_number)


        # Render the checkout page with the cart items and total price
        return render(request, self.template_name, {'cart_items': [], 'total_price': 0,
                                                    'cart_total': 0, 'cart_items_count': 0,
                                                    'products': products,
                                                    'customer': customer })
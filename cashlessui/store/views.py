from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Product, StockProductPurchase, StockProductSale, Customer
from decimal import Decimal
from django.db.models import Sum, F


def view_stock(request):
    product_infos = Product.objects.all()
    return render(request, 'store/view_stock.html', {'products': product_infos})


def add_new_product(request):
    if request.method == 'POST':
        # Members for the new product (ProductInfo)
        ean = request.POST.get('ean')
        name = request.POST.get('name')
        resell_price = Decimal(request.POST.get('resellprice'))

        Product.objects.create(ean=ean, name=name, stock_quantity=0, resell_price=resell_price)

        return HttpResponse(f"Product '{name}' added successfully.")
    return render(request, 'store/add_product.html')


def add_stock(request):
    if request.method == 'POST':
        ean = request.POST.get('ean')
        quantity = int(request.POST.get('quantity'))
        purchase_price = Decimal(request.POST.get('purchase_price'))
        try:
            # Create a new Product object with the given EAN if it does not exist
            product_info = Product.objects.get(ean=ean)

            #for s in range(stock):
            StockProductPurchase.objects.create(product=product_info,
                                                quantity=quantity,
                                                purchase_price=purchase_price,
                                                total_cost=purchase_price * quantity)
            # Count the number of units of the product with the given EAN
            quantity_bough = StockProductPurchase.objects.aggregate(quantity=Sum('quantity'))['quantity'] or 0
            #StockProductPurchase.objects.filter(product=product_info).count())
            quantity_sold = StockProductSale.objects.filter(product=product_info).count()
            quantity = quantity_bough - quantity_sold

            # Update the stock of the product with the given EAN
            product_info.stock_quantity = quantity
            product_info.save()
        except StockProductPurchase.DoesNotExist:
            return HttpResponse("Error: Product with the given EAN does not exist.")
    return render(request, 'store/add_stock.html', {'products': Product.objects.all()})


def make_sale(request):
    if request.method == 'POST':
        ean = request.POST.get('ean')
        quantity = int(request.POST.get('quantity'))
        sale_price = Decimal(request.POST.get('sale_price'))
        customer = request.POST.get('customer')

        try:
            product_info = Product.objects.get(ean=ean)
            for s in range(quantity):
                StockProductSale.objects.create(product_info=product_info,
                                                quantity=1,
                                                sale_price=sale_price,
                                                sold_to=customer)

            quantity_bough = StockProductPurchase.objects.filter(product=product_info).count()
            quantity_sold = StockProductSale.objects.filter(product=product_info).count()
            quantity = quantity_bough - quantity_sold

            # Update the stock of the product with the given EAN
            product_info.stock_quantity = quantity
            product_info.save()

        except StockProductPurchase.DoesNotExist:
            return HttpResponse("Error: Product with the given EAN does not exist.")
    return render(request, 'store/make_sale.html', {
        'products': Product.objects.all()
    })


def view_customers(request):
    """View to list all customers."""

    return render(request, 'store/view_customers.html', {'customers': customers})


def add_customer(request):
    """View to add a new customer."""
    customers = Customer.objects.all()
    if request.method == 'POST':
        card_number = request.POST.get('card_number')
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        balance = request.POST.get('balance')

        # Create and save the new customer
        Customer.objects.create(
            card_number=card_number,
            name=name,
            surname=surname,
            balance=balance
        )
        #return redirect('customer_list')  # Redirect to the customer list after adding

    return render(request, 'store/view_customers.html', {'customers': customers})


# old
def view_financial_summary(request):
    #total_revenue = Sale.objects.aggregate(total_revenue=Sum('revenue'))['total_revenue'] or 0
    #total_expenses = Sale.objects.aggregate(total_expense=Sum('expense'))['total_expense'] or 0
    #total_expenses = Stock.objects.aggregate(total_expense=Sum(F('quantity') * F('unit_price')))['total_expense'] or 0
    #total_earnings = total_revenue - total_expenses
    products_sold = StockProductPurchase.objects.filter(type='SOLD').all()
    products_bought = StockProductPurchase.objects.filter(type='BOUGHT').all()

    #sales = Sale.objects.all()
    #stock = Stock.objects.all()

    context = {
        #    'total_revenue': total_revenue,
        #    'total_expenses': total_expenses,
        #    'total_earnings': total_earnings,
        'products_sold': products_sold,
        'products_bought': products_bought,
        #    #'stock': stock,
    }
    return render(request, 'store/view_financial_summary.html', context)

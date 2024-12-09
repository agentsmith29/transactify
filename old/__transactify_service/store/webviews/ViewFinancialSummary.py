from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from cashlessui.models import Customer
from ..webmodels.CustomerDeposit import CustomerDeposit
from ..webmodels.CustomerBalance import CustomerBalance
from ..webmodels.CustomerPurchase import CustomerPurchase
from ..webmodels.ProductRestock import ProductRestock
import json

from ..webviews.ManageCustomerHelper import ManageCustomerHelper

#from ..apps import hwcontroller
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt, ensure_csrf_cookie

class ViewFinancialSummary(View):

    def get(self, request):     
        #     #total_revenue = Sale.objects.aggregate(total_revenue=Sum('revenue'))['total_revenue'] or 0
        #total_expenses = Sale.objects.aggregate(total_expense=Sum('expense'))['total_expense'] or 0
        #total_expenses = Stock.objects.aggregate(total_expense=Sum(F('quantity') * F('unit_price')))['total_expense'] or 0
        #total_earnings = total_revenue -ProductRestocktotal_expenses
        products_sold = ProductRestock.objects.filter().all()
        
        products_bought = CustomerPurchase.objects.filter().all()
        # revenue is the 
               #sales = Sale.objects.all()
        #stock = Stock.objects.all()

        context = {
            #'total_revenue': total_revenue,
            #'total_expenses': total_expenses,
            #'total_earnings': total_earnings,
            'products_sold': products_sold,
            'products_bought': products_bought,
            #    #'stock': stock,
        }
        return render(request, 'store/view_financial_summary.html', context)
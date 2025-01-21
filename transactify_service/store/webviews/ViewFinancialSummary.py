import json

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View

from store.webmodels.Customer import Customer

from ..webmodels.CustomerDeposit import CustomerDeposit
from ..webmodels.CustomerPurchase import CustomerPurchase
from ..webmodels.ProductRestock import ProductRestock
from ..webmodels.StoreProduct import StoreProduct
from store.helpers.ManageStockHelper import StoreHelper


#from ..apps import hwcontroller
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Sum

from transactify_service.settings import CONFIG
import logging


# import datetime
from datetime import datetime, timedelta


from datetime import datetime
from django.db.models import Sum
from django.db.models import Sum, F
from datetime import datetime, timedelta


class _TimeSpanProxy:
    def __init__(self, outer):
        self._outer = outer

    def __getattr__(self, name):
        """
        Redirect calls to the properties of the outer class,
        but with the timespan parameter automatically applied.
        """
        attr = getattr(self._outer, name)
        if callable(attr):
            def wrapper(*args, **kwargs):
                kwargs.setdefault('timespan', self._outer._timespan)
                return attr(*args, **kwargs)
            return wrapper
        return attr
    
class FinancialMetrics:
    def __init__(self, timespan: tuple[datetime, datetime] = None):
        self._timespan = timespan

    def get_revenue(self, timespan: tuple[datetime, datetime] = None):
        """Get the total revenue within a given timespan or all."""
        if timespan:
            return CustomerPurchase.objects.filter(issued_at__range=timespan).aggregate(Sum('revenue'))['revenue__sum'] or 0
        return CustomerPurchase.objects.aggregate(Sum('revenue'))['revenue__sum'] or 0

    def get_expenses(self, timespan: tuple[datetime, datetime] = None):
        """Get the total expenses within a given timespan or all."""
        # expenses are purchase_price*quantity
        if timespan:
            return ProductRestock.objects.filter(issued_at__range=timespan).aggregate(
                total_cost=Sum(F('purchase_price') * F('quantity'))
            )['total_cost'] or 0

        return ProductRestock.objects.aggregate(
            total_cost=Sum(F('purchase_price') * F('quantity'))
        )['total_cost'] or 0

    def get_earnings(self, timespan: tuple[datetime, datetime] = None):
        """Get the total earnings within a given timespan or all."""
        return self.get_revenue(timespan) - self.get_expenses(timespan)


    def get_financial_data(self, start_date=None, end_date=None):
        start_date = self._timespan[0] if start_date is None else start_date
        end_date = self._timespan[1] if end_date is None else end_date

        print(f"Fetching data from {start_date} to {end_date}")

        purchases = (
            CustomerPurchase.objects.filter(purchase_date__range=[start_date, end_date])
            .annotate(day=F("purchase_date__date"))
            .values("day")
            .annotate(total_revenue=Sum("revenue"), total_profit=Sum("profit"), total_cost=Sum("expenses"))
        )
        print(f"Purchases: {list(purchases)}\n\n")

        restocks = (
            ProductRestock.objects.filter(restock_date__range=[start_date, end_date])
            .annotate(day=F("restock_date__date"))
            .values("day")
            .annotate(total_cost=Sum("total_cost"))
        )
        print(f"Restocks: {list(restocks)}\n\n")

        results = {}
        for purchase in purchases:
            day = purchase["day"]
            results[day] = {
                "revenue": float(purchase["total_revenue"]),
                "profit": float(purchase["total_profit"]),
                "cost": float(purchase["total_cost"]),
            }


        #for restock in restocks:
        #    day = restock["day"]
        #    if day in results:
        #       results[day]["cost"] += float(restock["total_cost"])
        #    else:
        #        results[day] = {
        #            "revenue": float(restock["total_cost"]),
        #            "profit": 0.0,
        #            "cost": float(restock["total_cost"]),
        #        }
        # revenue is cost 

        sorted_results = dict(sorted(results.items(), key=lambda x: x[0]))

        chart_data = {
            "timestamps": [day.strftime("%Y-%m-%d") for day in sorted_results.keys()],
            "revenue": [data["revenue"] for data in sorted_results.values()],
            "cost": [data["cost"] for data in sorted_results.values()],
            "profit": [data["profit"] for data in sorted_results.values()],
        }
        print(chart_data)
        return chart_data


    @property
    def revenue(self):
        return self.get_revenue()

    @property
    def expenses(self):
        return self.get_expenses()

    @property
    def earnings(self):
        return self.get_earnings()

    @property
    def timespan(self):
        return self._TimeSpanProxy(self)



        

    


#from ..apps import hwcontroller
@method_decorator(login_required, name='dispatch')
class Summary(View):
    template_name = 'store/summary.html'

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f"{CONFIG.webservice.SERVICE_NAME}.webviews.{self.__class__.__name__}")
        super().__init__(**kwargs)

    def get_customers(self, timespan: tuple[datetime, datetime] = None):
        """ Get the number of customers within a given timespan or all.

        Args:
            timespan (tuple[datetime, datetime], optional): A tuple of two datetime objects representing the start and end of the timespan.

        Returns:
            QuerySet: A queryset of customers.
        """
        if timespan:
            return Customer.objects.filter(issued_at__range=timespan)
        return Customer.objects.all()

    def get_products(self):
        """ 
            Get the number of products which quatity is greater than 0 of a store within a given timespan or all.
        """
        return StoreProduct.objects.all()

    def get_purchases(self, timespan: tuple[datetime, datetime] = None):
        """ Get the number of purchases within a given timespan or all.

        Args:
            timespan (tuple[datetime, datetime], optional): A tuple of two datetime objects representing the start and end of the timespan.

        Returns:
            QuerySet: A queryset of purchases.
        """
        if timespan:
            return CustomerPurchase.objects.filter(purchase_date__range=timespan)
        return CustomerPurchase.objects.all()
    
    def get_restocks(self, timespan: tuple[datetime, datetime] = None):
        """ Get the number of restocks within a given timespan or all.

        Args:
            timespan (tuple[datetime, datetime], optional): A tuple of two datetime objects representing the start and end of the timespan.

        Returns:
            QuerySet: A queryset of restocks.
        """
        if timespan:
            return ProductRestock.objects.filter(restock_date__range=timespan)
        return ProductRestock.objects.all()
    
    # =================================================================================================================


    # =================================================================================================================
    # Dictionary of statistics
    # =================================================================================================================
    def get_customer_statistics(self, timespan: tuple[datetime, datetime] = None):
        """ Get statistics for customers within a given timespan or all.

        Args:
            timespan (tuple[datetime, datetime], optional): A tuple of two datetime objects representing the start and end of the timespan.

        Returns:
            dict: A dictionary of customer statistics.
        """
        return {
            'timespan': {
                'total': self.get_customers(timespan).count(),
            },
            'total': self.get_customers().count(),
        }
    
    def get_product_statistics(self, timespan: tuple[datetime, datetime] = None):
        """ Get statistics for products within a given timespan or all.

        Args:
            timespan (tuple[datetime, datetime], optional): A tuple of two datetime objects representing the start and end of the timespan.

        Returns:
            dict: A dictionary of product statistics.
        """
        return {
            'total': self.get_products().count(),
        }
    
    def get_purchase_statistics(self, timespan: tuple[datetime, datetime] = None):
        """ Get statistics for purchases within a given timespan or all.

        Args:
            timespan (tuple[datetime, datetime], optional): A tuple of two datetime objects representing the start and end of the timespan.

        Returns:
            dict: A dictionary of purchase statistics.
        """
        return {
            'timespan': {
                'total': self.get_purchases(timespan).count(),
            },
            'total': self.get_purchases().count(),
        }

    def get_restock_statistics(self, timespan: tuple[datetime, datetime] = None):
        """ Get statistics for restocks within a given timespan or all.

        Args:
            timespan (tuple[datetime, datetime], optional): A tuple of two datetime objects representing the start and end of the timespan.

        Returns:
            dict: A dictionary of restock statistics.
        """
        return {
            'timespan': {
                'total': self.get_restocks(timespan).count(),
            },
            'total': self.get_restocks().count(),
        }
    
    def get(self, request): 
 
        #     #total_revenue = Sale.objects.aggregate(total_revenue=Sum('revenue'))['total_revenue'] or 0
        #total_expenses = Sale.objects.aggregate(total_expense=Sum('expense'))['total_expense'] or 0
        #total_expenses = Stock.objects.aggregate(total_expense=Sum(F('quantity') * F('unit_price')))['total_expense'] or 0
        #total_earnings = total_revenue -ProductRestocktotal_expenses

        restock = ProductRestock.objects.filter().all()        
        purchases = CustomerPurchase.objects.filter().all()

        timespan_start = datetime.now()
        timespan_end = datetime.now() - timedelta(days=30)

        # Statistics for customers and products
        customer_statistics = self.get_customer_statistics((timespan_start, timespan_end))
        products_statistics = self.get_product_statistics((timespan_start, timespan_end))
        # Purchase and restock statistics
        purchases_statistics = self.get_purchase_statistics((timespan_start, timespan_end))
        restocks_statistics = self.get_restock_statistics((timespan_start, timespan_end))

        finm = FinancialMetrics((timespan_start, timespan_end))
        print(finm.get_financial_data(timespan_end, timespan_start))
        
        # Revenue, expenses and earnings, one word, different than finance
        context = {
            'customer': customer_statistics,
            'products': products_statistics,
            'purchases': purchases_statistics,
            'restocks': restocks_statistics,
            'financial_metrics': finm,
            'purchases_list': purchases,
            'restocks_list': restock,
            'chart_financial_data': finm.get_financial_data(timespan_end, timespan_start),
            'top_selling_products': StoreProduct.get_top_selling_products(5)
        }
        return render(request, self.template_name, context)
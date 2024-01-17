from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from marine.methods import (
    bill_alert_function,
    get_client_ip,
    salary_alert_function,
    store_alert_function,
    warehouse_alert_function,
)
from marine.computer.models import Computer
from marine.product.models import Product
from marine.shop.models import Sold, Store


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "marine/product/product_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get the shop instance
        computer = get_object_or_404(
            Computer, ip_address=str(get_client_ip(self.request))
        )
        shop = computer.shop
        # Set the alerts based on the user's staff status
        context["alert"] = (
            warehouse_alert_function()
            if self.request.user.is_staff
            else store_alert_function(shop)
        )
        context["bill_alert"] = bill_alert_function()

        # Set the salary_alert based on the user's staff status
        context["salary_alert"] = (
            salary_alert_function() if self.request.user.is_staff else None
        )
        # get the store and the sold

        context["store"] = Store.objects.get(product=context["object"], shop=shop)
        context["sold"] = Sold.objects.get(product=context["object"], shop=shop)

        return context

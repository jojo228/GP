from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import (
    DetailView,
)
from marine.computer.models import Computer

from marine.methods import (
    bill_alert_function,
    get_client_ip,
    salary_alert_function,
    store_alert_function,
    warehouse_alert_function,
)
from marine.sale.billing.model import Billing
from marine.sale.models import Sale, SaleItem


class SaleDetailView(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = "marine/sale/sale_detail.html"
    context_object_name = "sale"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        computer = get_object_or_404(Computer, ip_address=get_client_ip(self.request))
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

        context["items"] = SaleItem.objects.filter(
            sale_id=self.kwargs["pk"], is_original=True
        )
        return context


class SalePrintView(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = "marine/sale/sale_print.html"
    context_object_name = "sale"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        items = SaleItem.objects.filter(sale_id=self.kwargs["pk"], is_original=True)

        context["items"] = items

        context["billings"] = Billing.objects.filter(sale_id=self.kwargs["pk"])[:1]

        return context


class DeliveryPrintView(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = "marine/sale/delivery_print.html"
    context_object_name = "sale"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        items = SaleItem.objects.filter(sale_id=self.kwargs["pk"], is_original=True)

        context["items"] = items
        return context

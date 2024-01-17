import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import (
    ListView,
)

from marine.sale.billing.model import Billing
from marine.computer.models import Computer
from marine.methods import (
    bill_alert_function,
    get_client_ip,
    salary_alert_function,
    store_alert_function,
    warehouse_alert_function,
)
from marine.sale.models import Sale


class BillingListView(LoginRequiredMixin, ListView):
    model = Billing
    template_name = "marine/billing/billing_list.html"
    context_object_name = "billings"

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
        context["sale"] = Sale.objects.get(id=self.kwargs["sale_id"])
        
        ## add a variable to check if amount_left = 0
        # first get list of debt billings and then retrieve the last one, to get the amount_left
        billings = Billing.objects.filter(sale=context["sale"])
        context["has_amount_left"] = True
        if bool(billings):
            billing = billings.order_by("payment_date").reverse()[0]
            # set the variable no_amount_left to if amount_left = 0 or not
            context["has_amount_left"] = billing.amount_left != 0

        return context

    def get_queryset(self):
        return Billing.objects.filter(sale_id=self.kwargs["sale_id"])


class BillingAlertListView(LoginRequiredMixin, ListView):
    model = Billing
    template_name = "marine/billing/billing_alert_list.html"
    context_object_name = "billings"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        computer = get_object_or_404(Computer, ip_address=get_client_ip(self.request))
        shop = computer.shop
        if self.request.user.is_staff:
            context["alert"] = warehouse_alert_function()
        else:
            context["alert"] = store_alert_function(shop)
            context["bill_alert"] = bill_alert_function()

        return context

    def get_queryset(self):
        todays_date = datetime.date.today()
        return Billing.objects.filter(next_payment_date=todays_date)

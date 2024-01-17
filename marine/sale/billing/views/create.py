from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
)

from marine.sale.billing.forms import BillingForm
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


class BillingCreateView(LoginRequiredMixin, CreateView):
    model = Billing
    form_class = BillingForm
    template_name = "marine/billing/billing_create.html"

    def form_valid(self, form):
        sale = Sale.objects.get(id=self.kwargs["sale_id"])
        form.instance.added_by = self.request.user.employee
        form.instance.sale = sale
        form.instance.customer = sale.customer
        return super(BillingCreateView, self).form_valid(form)

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
        try:
            context["last_billing"] = (
                context["sale"].billings.all().order_by("payment_date").reverse()[0]
            )
        except IndexError:
            pass
        return context

    def get_success_url(self):
        self.object.validate_bill
        return reverse("list_billing", args=[self.kwargs["sale_id"]])

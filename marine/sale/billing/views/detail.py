from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import (
    DetailView,
)
from django.db.models import F
from marine.sale.billing.model import Billing
from marine.computer.models import Computer
from marine.methods import (
    bill_alert_function,
    get_client_ip,
    salary_alert_function,
    store_alert_function,
    warehouse_alert_function,
)


class BillingDetailView(LoginRequiredMixin, DetailView):
    model = Billing
    template_name = "marine/billing/billing_detail.html"
    context_object_name = "billing"

    def get_queryset(self):
        return Billing.objects.filter(id=self.kwargs["pk"]).values(
            Numero_Facture=F("sale__bill_number"),
            Nom_du_client=F("sale__customer__name"),
            Date_de_la_facture=F("sale__date_created"),
            Montant_total=F("sale__total_amount"),
            Date_de_paiement=F("payment_date"),
            Montant_payé=F("amount_paid"),
            Date_prochain_paiement=F("next_payment_date"),
            Montant_restant=F("amount_left"),
        )

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

        context["billing_object"] = Billing.objects.get(id=self.kwargs["pk"])
        return context


class BillingPrintView(LoginRequiredMixin, DetailView):
    model = Billing
    template_name = "marine/billing/billing_print.html"

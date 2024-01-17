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
from marine.views import SuperUserRequiredMixin


class ComputerDetailView(SuperUserRequiredMixin, DetailView):
    model = Computer
    template_name = "marine/computer/computer_detail.html"
    context_object_name = "computer"

    def get_queryset(self):
        return Computer.objects.filter(id=self.kwargs["pk"]).values(
            "ip_address",
            "name",
            "shop__name",
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

        context["computer_object"] = Computer.objects.get(id=self.kwargs["pk"])
        return context

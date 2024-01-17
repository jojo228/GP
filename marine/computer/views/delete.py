from django.db.models import deletion
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    DeleteView,
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


class ComputerDeleteView(SuperUserRequiredMixin, DeleteView):
    model = Computer
    success_url = reverse_lazy("list_computer")
    template_name = "marine/computer/computer_confirm_delete.html"

    def delete(self, *args, **kwargs):
        try:
            return super(ComputerDeleteView, self).delete(*args, **kwargs)
        except deletion.ProtectedError:
            pass

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
        return context

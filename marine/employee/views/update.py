from django.shortcuts import get_object_or_404
from django.views.generic import UpdateView

from marine.employee.forms import EmployeeMultiForm
from marine.employee.models import Employee
from marine.methods import (
    bill_alert_function,
    get_client_ip,
    salary_alert_function,
    store_alert_function,
    warehouse_alert_function,
)
from marine.computer.models import Computer
from marine.views import AdminStaffRequiredMixin


class EmployeeUpdateView(AdminStaffRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeMultiForm
    template_name = "marine/employee/employee_update.html"

    def get_form_kwargs(self):
        kwargs = super(EmployeeUpdateView, self).get_form_kwargs()
        kwargs.update(
            instance={
                "employee": self.object,
                "user": self.object.user,
            }
        )
        return kwargs

    def get_success_url(self):
        return reverse("detail_product", args=[self.object["employee"].pk])

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

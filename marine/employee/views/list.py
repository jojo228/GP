import datetime
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

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

# This view displays a list of all employees in a grid


class EmployeeListView(AdminStaffRequiredMixin, ListView):
    model = Employee
    template_name = "marine/employee/employee_list.html"

    def get_queryset(self):
        keyword = self.request.GET.get("search")
        object_list = Employee.objects.all()
        if keyword:
            object_list = object_list.filter(
                Q(contact__contains=keyword)
                | Q(user__first_name__icontains=keyword)
                | Q(user__last_name__icontains=keyword)
            )
        return object_list

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


class EmployeeAlertListView(AdminStaffRequiredMixin, ListView):
    model = Employee
    template_name = "marine/employee/employee_salary_alert.html"

    def get_queryset(self):
        keyword = self.request.GET.get("search")
        todays_date = datetime.date.today().day
        object_list = Employee.objects.filter(salary_payment_date__day=todays_date)
        if keyword:
            object_list = object_list.filter(
                Q(contact__contains=keyword)
                | Q(user__first_name__icontains=keyword)
                | Q(user__last_name__icontains=keyword)
            )
        return object_list

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

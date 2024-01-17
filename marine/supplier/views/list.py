from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import (
    ListView,
)

from marine.methods import (
    bill_alert_function,
    get_client_ip,
    salary_alert_function,
    store_alert_function,
    warehouse_alert_function,
)
from marine.computer.models import Computer
from marine.supplier.models import Supplier
from marine.views import AdminStaffRequiredMixin


class SupplierListView(AdminStaffRequiredMixin, ListView):
    model = Supplier
    template_name = "marine/supplier/supplier_list.html"

    def get_queryset(self):
        keyword = self.request.GET.get("search")
        object_list = Supplier.objects.all()
        if keyword:
            object_list = object_list.filter(
                Q(contact__contains=keyword) | Q(company_name__icontains=keyword)
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

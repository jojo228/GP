from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from marine.methods import (
    bill_alert_function,
    get_client_ip,
    salary_alert_function,
    store_alert_function,
    warehouse_alert_function,
)
from marine.computer.models import Computer
from marine.views import AdminStaffRequiredMixin
from marine.supply.models import Supply


class SupplyListView(AdminStaffRequiredMixin, ListView):
    model = Supply
    template_name = "marine/supply/supply_list.html"
    paginate_by = 50

    def get_queryset(self):
        keyword = self.request.GET.get("search")

        # Query the Supply objects and order them by date_created in descending order
        queryset = Supply.objects.filter(
            Q(is_temporary=False)
            | (Q(is_temporary=True) & Q(added_by=self.request.user.employee))
        ).order_by("-date_created")

        if keyword:
            # Apply keyword filtering on various fields using OR operator
            queryset = queryset.filter(
                Q(bill_number__contains=keyword)
                | Q(supervised_by__user__first_name__icontains=keyword)
                | Q(added_by__user__first_name__icontains=keyword)
                | Q(supervised_by__user__last_name__icontains=keyword)
                | Q(added_by__user__last_name__icontains=keyword)
                | Q(supplier__company_name__icontains=keyword)
                | Q(supplier__contact__contains=keyword)
            )
        return queryset

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

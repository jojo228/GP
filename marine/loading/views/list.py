from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from marine.loading.models import Loading
from marine.methods import (
    bill_alert_function,
    get_client_ip,
    salary_alert_function,
    store_alert_function,
    warehouse_alert_function,
)
from marine.computer.models import Computer


class LoadingListView(LoginRequiredMixin, ListView):
    model = Loading
    template_name = "marine/loading/loading_list.html"
    paginate_by = 50

    def get_queryset(self):
        # Retrieve the keyword typed through the search bar
        keyword = self.request.GET.get("search")

        # Retrieve the actual shop using its MAC address
        # and filter the sales' list
        computer = get_object_or_404(Computer, ip_address=get_client_ip(self.request))
        shop = computer.shop

        # Create a base queryset with filtering conditions
        base_queryset = Loading.objects.filter(
            Q(is_temporary=False) | (Q(is_temporary=True) & Q(added_by=self.request.user.employee))
        )

        # Apply filtering based on user and shop conditions
        if not self.request.user.is_staff:
            base_queryset = base_queryset.filter(shop=shop)

        # Apply keyword search filters if a keyword is provided
        if keyword:
            base_queryset = base_queryset.filter(
                Q(bill_number__contains=keyword) |
                Q(supervised_by__user__first_name__icontains=keyword) |
                Q(added_by__user__first_name__icontains=keyword) |
                Q(supervised_by__user__last_name__icontains=keyword) |
                Q(added_by__user__last_name__icontains=keyword) |
                Q(shop__name__icontains=keyword)
            )

        # Apply ordering based on the date_created field
        object_list = base_queryset.order_by("-date_created")

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

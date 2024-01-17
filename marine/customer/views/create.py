from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
)
from marine.customer.forms import CustomerForm
from marine.customer.models import Customer


from marine.methods import (
    bill_alert_function,
    get_client_ip,
    salary_alert_function,
    store_alert_function,
    warehouse_alert_function,
)

from marine.views import AdminStaffRequiredMixin


class CustomerCreateView(AdminStaffRequiredMixin, CreateView):
    form_class = CustomerForm
    template_name = "marine/customer_create.html"

    def get_queryset(self):
        keyword = self.request.GET.get("search")
        object_list = Customer.objects.all()
        if keyword:
            object_list = object_list.filter(
                Q(contact__contains=keyword) | Q(name__icontains=keyword)
            )
        return object_list

    def get_success_url(self):
        return reverse("detail_customer", kwargs={"pk": self.object.pk})

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

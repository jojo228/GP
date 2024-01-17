from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView

from marine.methods import (
    bill_alert_function,
    get_client_ip,
    salary_alert_function,
    store_alert_function,
    warehouse_alert_function,
)
from marine.computer.models import Computer
from marine.product.forms import ProductMultiForm
from marine.shop.models import Shop, Sold, Store
from marine.views import AdminStaffRequiredMixin


class ProductCreateView(AdminStaffRequiredMixin, CreateView):
    form_class = ProductMultiForm
    template_name = "marine/product/product_create.html"

    def get_success_url(self):
        # retrieve the shop
        computer = get_object_or_404(Computer, ip_address=get_client_ip(self.request))
        shop = computer.shop
        # get or create a store instance
        form_store = self.object["store"]
        product = self.object["product"]
        store, _ = Store.objects.get_or_create(product=product, shop=shop)
        store.quantity_alert = form_store.quantity_alert
        store.save()
        # loop the shops
        for shop in Shop.objects.all():
            # get or create a store instance
            Store.objects.get_or_create(product=product, shop=shop)
            # get or create a sold instance
            Sold.objects.get_or_create(product=product, shop=shop)
        return reverse_lazy("list_product")

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

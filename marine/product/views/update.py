from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import UpdateView

from marine.methods import (
    bill_alert_function,
    get_client_ip,
    salary_alert_function,
    store_alert_function,
    warehouse_alert_function,
)
from marine.computer.models import Computer
from marine.product.forms import ProductMultiForm
from marine.product.models import Product, Warehouse
from marine.shop.models import Shop, Sold, Store
from marine.views import AdminStaffRequiredMixin


class ProductUpdateView(AdminStaffRequiredMixin, UpdateView):
    model = Product
    form_class = ProductMultiForm
    template_name = "marine/product/product_update.html"

    def get_form_kwargs(self):
        # get the shop instance
        computer = get_object_or_404(
            Computer, ip_address=str(get_client_ip(self.request))
        )
        shop = computer.shop
        kwargs = super(ProductUpdateView, self).get_form_kwargs()
        kwargs.update(
            instance={
                "product": self.object,
                "store": Store.objects.get(product=self.object, shop=shop),
                "warehouse": self.object.marine_warehouse_related,
            }
        )

        return kwargs

    def get_success_url(self):
        # retrieve the shop
        computer = get_object_or_404(Computer, ip_address=get_client_ip(self.request))
        shop = computer.shop
        # get or create a store instance
        form_store = self.object["store"]
        product = self.object["product"]
        form_warehouse = self.object["warehouse"]
        warehouse, _ = Warehouse.objects.get_or_create(product=product)
        warehouse.quantity = form_warehouse.quantity
        warehouse.save()
        store, _ = Store.objects.get_or_create(product=product, shop=shop)
        store.quantity_alert = form_store.quantity_alert
        store.quantity = form_store.quantity
        store.save()
        # Loop through all shops and update quantities
        for shop in Shop.objects.all():
            if shop != computer.shop:  # Skip the current shop
                store, _ = Store.objects.get_or_create(product=product, shop=shop)
                store.quantity_alert = form_store.quantity_alert
                store.quantity = form_store.quantity
                store.save()
                Sold.objects.get_or_create(product=product, shop=shop)
        return reverse("detail_product", args=[product.id])

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

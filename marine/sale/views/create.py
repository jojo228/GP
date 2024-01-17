from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.views.generic.base import RedirectView

from marine.computer.models import Computer
from marine.customer.models import Customer
from marine.methods import (
    bill_alert_function,
    get_client_ip,
    salary_alert_function,
    store_alert_function,
    warehouse_alert_function,
)
from marine.product.models import Product
from marine.sale.forms import SaleItemForm, SaleMultiForm
from marine.sale.models import Sale, SaleItem

# variables
sale_create_template = "marine/sale/sale_create.html"


class SaleInitiateView(LoginRequiredMixin, RedirectView):
    pattern_name = "create_sale_list_saleitem"


class SaleValidateView(LoginRequiredMixin, UpdateView):
    model = Sale
    form_class = SaleMultiForm
    template_name = sale_create_template

    def get_form_kwargs(self):
        kwargs = super(SaleValidateView, self).get_form_kwargs()
        kwargs.update(
            instance={
                "sale": self.object,
                "customer": self.object.customer,
            }
        )
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # retrieve shop
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
        # parameters or data
        context["sale_id"] = self.kwargs["pk"]
        context["items"] = SaleItem.objects.filter(
            sale_id=self.kwargs["pk"], is_original=True
        )
        context["total_amount"] = context["items"].aggregate(Sum("total_amount"))[
            "total_amount__sum"
        ]

        # form
        context["item_form"] = SaleItemForm()
        context["sale_form"] = context["form"]

        # for autocomplete
        product_json = list(
            Product.objects.filter(marine_stores__shop=shop).values(
                "id",
                "designation",
                "unit_price",
                "marine_stores__quantity",
            )
        )
        context["products_data"] = product_json
        customer_json = list(
            Customer.objects.values(
                "id",
                "name",
                "contact",
            )
        )
        context["customers_data"] = customer_json

        return context

    def get_success_url(self):
        self.object["sale"].validate_bill
        return reverse("detail_sale", args=[self.kwargs["pk"]])


class SaleCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # retrieve shop
        computer = get_object_or_404(Computer, ip_address=get_client_ip(self.request))
        shop = computer.shop
        if kwargs.get("pk") is None:
            sale = Sale.objects.create(
                added_by=self.request.user.employee,
                shop=shop,
            )
            kwargs["sale_id"] = sale.id
        else:
            # transform "pk" to "sale_id"
            kwargs["sale_id"] = kwargs["pk"]
            del kwargs["pk"]
        view = SaleInitiateView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = SaleValidateView.as_view()
        return view(request, *args, **kwargs)


class SaleItemListView(LoginRequiredMixin, ListView):
    model = SaleItem
    template_name = sale_create_template
    context_object_name = "items"

    def get_queryset(self):
        return SaleItem.objects.filter(sale_id=self.kwargs["sale_id"], is_original=True).order_by("-id")

    def get_context_data(self):
        context = super().get_context_data()

        # retrieve shop
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

        saleitems = SaleItem.objects.filter(
            sale_id=self.kwargs["sale_id"], is_original=True
        )

        # parameters for the template
        if saleitems:
            context["total_amount"] = saleitems.aggregate(Sum("total_amount"))[
                "total_amount__sum"
            ]
        else:
            context["total_amount"] = 0
        context["sale_id"] = self.kwargs["sale_id"]

        sale = Sale.objects.get(id=self.kwargs["sale_id"])
        

        # form to display
        context["item_form"] = SaleItemForm()
        context["sale_form"] = SaleMultiForm(
            instance={
                "customer": sale.customer,
                "sale": sale,
            }
        )

        # for autocomplete
        product_json = list(
            Product.objects.filter(marine_stores__shop=shop).values(
                "id",
                "designation",
                "unit_price",
                "marine_stores__quantity",
            )
        )

        context["products_data"] = product_json
        customer_json = list(
            Customer.objects.values(
                "id",
                "name",
                "contact",
            )
        )
        context["customers_data"] = customer_json

        return context


# create


class SaleItemCreateView(LoginRequiredMixin, CreateView):
    model = SaleItem
    form_class = SaleItemForm
    template_name = sale_create_template

    def form_valid(self, form):
        try:
            quantity = form.instance.quantity
            form.instance = SaleItem.objects.get(
                sale_id=self.kwargs["sale_id"],
                product=form.instance.product,
                is_original=True,
            )
            form.instance.quantity += quantity
        except SaleItem.DoesNotExist:
            form.instance.sale_id = self.kwargs["sale_id"]

        return super(SaleItemCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sale_form"] = SaleMultiForm()
        context["item_form"] = context["form"]
        context["sale_id"] = self.kwargs["sale_id"]

        # retrieve shop
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
        # for autocomplete
        product_json = list(
            Product.objects.filter(marine_stores__shop=shop).values(
                "id",
                "designation",
                "unit_price",
                "marine_stores__quantity",
            )
        )
        context["products_data"] = product_json
        customer_json = list(
            Customer.objects.values(
                "id",
                "name",
                "contact",
            )
        )
        context["customers_data"] = customer_json

        return context

    def get_success_url(self):
        return reverse("create_sale_list_saleitem", args=[self.kwargs["sale_id"]])


# update


class SaleItemUpdateView(LoginRequiredMixin, UpdateView):
    model = SaleItem
    form_class = SaleItemForm
    template_name = sale_create_template

    def form_valid(self, form):
        try:
            quantity = form.instance.quantity
            form.instance = SaleItem.objects.get(
                sale_id=self.kwargs["sale_id"],
                product=form.instance.product,
                is_original=True,
            )
            if form.instance.pk == self.object.pk:
                form.instance.price = self.object.price
                form.instance.discount_price = self.object.discount_price
                form.instance.quantity = quantity
            else:
                form.instance.quantity += quantity
                self.object.delete()
        except SaleItem.DoesNotExist:
            form.instance.sale_id = self.kwargs["sale_id"]
            self.object.delete()

        return super(SaleItemUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # retrieve shop
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
        context["sale_id"] = self.kwargs["sale_id"]
        context["items"] = SaleItem.objects.filter(
            sale_id=self.kwargs["sale_id"],
            is_original=True,
        ).exclude(id=self.kwargs["pk"])

        sale = Sale.objects.get(id=self.kwargs["sale_id"])
        

        context["sale_form"] = SaleMultiForm(
            instance={
                "sale": sale,
                "customer": sale.customer,
            }
        )
        context["item_form"] = context["form"]

        # for autocomplete
        product_json = list(
            Product.objects.filter(marine_stores__shop=shop).values(
                "id",
                "designation",
                "unit_price",
                "marine_stores__quantity",
            )
        )
        context["products_data"] = product_json
        customer_json = list(
            Customer.objects.values(
                "id",
                "name",
                "contact",
            )
        )
        context["customers_data"] = customer_json

        return context

    def get_success_url(self):
        return reverse("create_sale_list_saleitem", args=[self.kwargs["sale_id"]])


# delete


class SaleItemDeleteView(LoginRequiredMixin, DeleteView):
    model = SaleItem
    context_object_name = "saleitem"
    template_name = "marine/sale/saleitem_confirm_delete.html"

    def get_success_url(self):
        return reverse("create_sale_list_saleitem", args=[self.kwargs["sale_id"]])

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

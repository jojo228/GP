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
sale_update_template = "marine/sale/sale_update.html"


class InitiateSaleUpdateView(LoginRequiredMixin, RedirectView):
    pattern_name = "update_sale_list_saleitem"


class ValidateSaleUpdateView(LoginRequiredMixin, UpdateView):
    model = Sale
    form_class = SaleMultiForm
    template_name = sale_update_template

    def get_form_kwargs(self):
        kwargs = super(ValidateSaleUpdateView, self).get_form_kwargs()
        kwargs.update(
            instance={
                "customer": self.object.customer,
                "sale": self.object,
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
        sale = Sale.objects.get(id=self.kwargs["pk"])

        # delete original saleitems
        for is_original_saleitem in sale.item.filter(is_original=True):
            is_original_saleitem.delete()

        # transform copied saleitems to original
        for copied_saleitem in sale.item.filter(is_original=False):
            copied_saleitem.is_original = True
            copied_saleitem.save()

        sale.validate_bill
        return reverse("detail_sale", args=[sale.id])


class SaleUpdateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # get the sale being updated
        sale = Sale.objects.get(id=self.kwargs["pk"])

        # check if there are already copied saleitems
        exist_copied_saleitems = sale.item.filter(is_original=False)

        # if they exist do nothing, if not set new ones
        if not exist_copied_saleitems:
            # get a copy of original saleitems
            copied_saleitems = sale.item.filter(is_original=True)

            # reset the instances to new instances
            for copied_saleitem in copied_saleitems:
                copied_saleitem.pk = None
                copied_saleitem._state.adding = True
                copied_saleitem.is_temporary = True  # to avoid altering the database
                copied_saleitem.is_original = False  # set to copied
                copied_saleitem.save()

            # link copied saleitems to sale
            sale.item.set(copied_saleitems)

        # set the sale id in kwargs
        kwargs["sale_id"] = sale.id

        # don't know yet why this
        del kwargs["pk"]

        view = InitiateSaleUpdateView.as_view()

        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ValidateSaleUpdateView.as_view()
        return view(request, *args, **kwargs)


class CancelSaleUpdateView(LoginRequiredMixin, RedirectView):
    pattern_name = "detail_sale"

    def get_redirect_url(self, *args, **kwargs):
        sale = Sale.objects.get(id=self.kwargs["pk"])

        # delete copied saleitems
        for copied_saleitem in sale.item.filter(is_original=False):
            copied_saleitem.delete()

        return super().get_redirect_url(*args, **kwargs)


### Sales Items ###


# list
class UpdateSaleSaleItemListView(LoginRequiredMixin, ListView):
    model = SaleItem
    template_name = sale_update_template
    context_object_name = "items"

    def get_queryset(self):
        return SaleItem.objects.filter(
            sale_id=self.kwargs["sale_id"], is_original=False
        ).order_by("-id")

    def get_context_data(self):
        context = super().get_context_data()

        # retrieve shop
        computer = get_object_or_404(Computer, ip_address=get_client_ip(self.request))
        shop = computer.shop

        saleitems = SaleItem.objects.filter(
            sale_id=self.kwargs["sale_id"], is_original=False
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
        context["alert"] = warehouse_alert_function()
        context["bill_alert"] = bill_alert_function()

        ## form to display
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
class UpdateSaleSaleItemCreateView(LoginRequiredMixin, CreateView):
    model = SaleItem
    form_class = SaleItemForm
    template_name = sale_update_template

    def form_valid(self, form):
        try:
            quantity = form.instance.quantity
            form.instance = SaleItem.objects.get(
                sale_id=self.kwargs["sale_id"],
                product=form.instance.product,
                is_original=False,
            )
            form.instance.quantity += quantity
        except SaleItem.DoesNotExist:
            form.instance.sale_id = self.kwargs["sale_id"]

        form.instance.is_original = False

        return super(UpdateSaleSaleItemCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # retrieve shop
        computer = get_object_or_404(Computer, ip_address=get_client_ip(self.request))
        shop = computer.shop

        ## parameters or data
        context["sale_id"] = self.kwargs["sale_id"]
        context["alert"] = warehouse_alert_function()
        context["bill_alert"] = bill_alert_function()

        # forms
        context["sale_form"] = SaleMultiForm()
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
        return reverse(
            "update_sale_list_saleitem",
            args=[
                self.kwargs["sale_id"],
            ],
        )


# update
class UpdateSaleSaleItemUpdateView(LoginRequiredMixin, UpdateView):
    model = SaleItem
    form_class = SaleItemForm
    template_name = sale_update_template

    def form_valid(self, form):
        try:
            quantity = form.instance.quantity
            form.instance = SaleItem.objects.get(
                sale_id=self.kwargs["sale_id"],
                product=form.instance.product,
                is_original=False,
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

        return super(UpdateSaleSaleItemUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # retrieve shop
        computer = get_object_or_404(Computer, ip_address=get_client_ip(self.request))
        shop = computer.shop

        ## parameters or data
        context["sale_id"] = self.kwargs["sale_id"]
        context["items"] = SaleItem.objects.filter(
            sale_id=self.kwargs["sale_id"], is_original=False
        ).exclude(id=self.kwargs["pk"])

        sale = Sale.objects.get(id=self.kwargs["sale_id"])
        context["alert"] = warehouse_alert_function()
        context["bill_alert"] = bill_alert_function()

        ## forms
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
        return reverse(
            "update_sale_list_saleitem",
            args=[
                self.kwargs["sale_id"],
            ],
        )


# delete
class UpdateSaleSaleItemDeleteView(LoginRequiredMixin, DeleteView):
    model = SaleItem
    context_object_name = "saleitem"
    template_name = "marine/sale/sale_update_saleitem_confirm_delete.html"

    def get_success_url(self):
        return reverse(
            "update_sale_list_saleitem",
            args=[
                self.kwargs["sale_id"],
            ],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["alert"] = warehouse_alert_function()
        context["bill_alert"] = bill_alert_function()
        return context

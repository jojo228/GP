from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.views.generic.base import RedirectView

from marine.computer.models import Computer
from marine.methods import (
    bill_alert_function,
    get_client_ip,
    salary_alert_function,
    store_alert_function,
    warehouse_alert_function,
)
from marine.product.models import Product
from marine.supplier.models import Supplier
from marine.supply.forms import SupplyItemForm, SupplyMultiForm
from marine.supply.models import Supply, SupplyItem
from marine.views import AdminStaffRequiredMixin

# variables
supply_update_template = "marine/supply/supply_update.html"


class InitiateSupplyUpdateView(AdminStaffRequiredMixin, RedirectView):
    pattern_name = "update_supply_list_supplyitem"


class ValidateSupplyUpdateView(AdminStaffRequiredMixin, UpdateView):
    model = Supply
    form_class = SupplyMultiForm
    template_name = supply_update_template

    def get_form_kwargs(self):
        kwargs = super(ValidateSupplyUpdateView, self).get_form_kwargs()
        kwargs.update(
            instance={
                "supply": self.object,
                "supplier": self.object.supplier,
            }
        )
        return kwargs

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

        # get the actual and filter keyword
        keyword = self.request.GET.get("search")
        items = SupplyItem.objects.filter(
            supply_id=self.kwargs["pk"], is_original=False
        )

        if keyword:
            items = items.filter(Q(product_designation__icontains=keyword))

        # parameters or data
        context["supply_id"] = self.kwargs["pk"]
        context["items"] = items
        context["total_amount"] = context["items"].aggregate(Sum("total_amount"))[
            "total_amount__sum"
        ]

        # form
        context["item_form"] = SupplyItemForm()
        context["supply_form"] = context["form"]

        # for autocomplete
        product_json = list(
            Product.objects.values(
                "id",
                "designation",
                "unit_price",
                "marine_warehouses__quantity",
            )
        )
        context["products_data"] = product_json
        supplier_json = list(
            Supplier.objects.values(
                "company_name",
                "contact",
            )
        )
        context["suppliers_data"] = supplier_json

        return context

    def get_success_url(self):
        supply = Supply.objects.get(id=self.kwargs["pk"])

        # delete original supplyitems
        for is_original_supplyitem in supply.item.filter(is_original=True):
            is_original_supplyitem.delete()

        # transform copied supplyitems to original
        for copied_supplyitem in supply.item.filter(is_original=False):
            copied_supplyitem.is_original = True
            copied_supplyitem.save()

        # reset the bill as temporary and save
        supply.validate_bill
        return reverse("detail_supply", args=[supply.id])


class SupplyUpdateView(AdminStaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # get the supply being updated
        supply = Supply.objects.get(id=self.kwargs["pk"])

        # check if there are aldetaily copied supplyitems
        exist_copied_supplyitems = supply.item.filter(is_original=False)

        # if they exist do nothing, if not set new ones
        if not exist_copied_supplyitems:
            # get a copy of original supplyitems
            copied_supplyitems = supply.item.filter(is_original=True)

            # reset the instances to new instances
            for copied_supplyitem in copied_supplyitems:
                copied_supplyitem.pk = None
                copied_supplyitem._state.adding = True
                copied_supplyitem.is_temporary = True  # to avoid altering the database
                copied_supplyitem.is_original = False  # set to copied
                copied_supplyitem.save()

            # link copied supplyitems to supply
            supply.item.set(copied_supplyitems)

        kwargs["supply_id"] = supply.id
        del kwargs["pk"]

        view = InitiateSupplyUpdateView.as_view()

        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ValidateSupplyUpdateView.as_view()
        return view(request, *args, **kwargs)


class CancelSupplyUpdateView(LoginRequiredMixin, RedirectView):
    pattern_name = "detail_supply"

    def get_redirect_url(self, *args, **kwargs):
        supply = Supply.objects.get(id=self.kwargs["pk"])

        # delete copied supplyitems
        for copied_supplyitem in supply.item.filter(is_original=False):
            copied_supplyitem.delete()

        return super().get_redirect_url(*args, **kwargs)


### Supply Items ###


# list
class SupplyUpdateSupplyItemListView(LoginRequiredMixin, ListView):
    model = SupplyItem
    template_name = supply_update_template
    context_object_name = "items"

    def get_queryset(self):
        return SupplyItem.objects.filter(
            supply_id=self.kwargs["supply_id"], is_original=False
        ).order_by("-id")

    def get_context_data(self):
        context = super().get_context_data()

        supply_items = SupplyItem.objects.filter(
            supply_id=self.kwargs["supply_id"], is_original=False
        )

        # parameters for the template
        if supply_items:
            context["total_amount"] = supply_items.aggregate(Sum("total_amount"))[
                "total_amount__sum"
            ]
        else:
            context["total_amount"] = 0
        context["supply_id"] = self.kwargs["supply_id"]

        supply = Supply.objects.get(id=self.kwargs["supply_id"])

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

        ## form to display
        context["item_form"] = SupplyItemForm()
        context["supply_form"] = SupplyMultiForm(
            instance={
                "supplier": supply.supplier,
                "supply": supply,
            }
        )

        # for autocomplete
        product_json = list(
            Product.objects.values(
                "id",
                "designation",
                "unit_price",
                "marine_warehouses__quantity",
            )
        )
        context["products_data"] = product_json
        supplier_json = list(
            Supplier.objects.values(
                "company_name",
                "contact",
            )
        )
        context["suppliers_data"] = supplier_json

        return context


# create


class SupplyUpdateSupplyItemCreateView(LoginRequiredMixin, CreateView):
    model = SupplyItem
    form_class = SupplyItemForm
    template_name = supply_update_template

    def form_valid(self, form):
        try:
            quantity = form.instance.quantity
            form.instance = SupplyItem.objects.get(
                supply_id=self.kwargs["supply_id"],
                product=form.instance.product,
                is_original=False,
            )
            form.instance.quantity += quantity
        except SupplyItem.DoesNotExist:
            form.instance.supply_id = self.kwargs["supply_id"]

        form.instance.is_original = False

        return super(SupplyUpdateSupplyItemCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ## parameters or data
        context["supply_id"] = self.kwargs["supply_id"]

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

        # forms
        context["supply_form"] = SupplyMultiForm()
        context["item_form"] = context["form"]

        # for autocomplete
        product_json = list(
            Product.objects.values(
                "id",
                "designation",
                "unit_price",
                "marine_warehouses__quantity",
            )
        )
        context["products_data"] = product_json
        supplier_json = list(
            Supplier.objects.values(
                "company_name",
                "contact",
            )
        )
        context["suppliers_data"] = supplier_json

        return context

    def get_success_url(self):
        return reverse(
            "update_supply_list_supplyitem",
            args=[self.kwargs["supply_id"]],
        )


# update
class SupplyUpdateSupplyItemUpdateView(LoginRequiredMixin, UpdateView):
    model = SupplyItem
    form_class = SupplyItemForm
    template_name = supply_update_template

    def form_valid(self, form):
        try:
            quantity = form.instance.quantity
            form.instance = SupplyItem.objects.get(
                supply_id=self.kwargs["supply_id"],
                product=form.instance.product,
                is_original=False,
            )
            if form.instance.pk == self.object.pk:
                form.instance.price = self.object.price
                form.instance.quantity = quantity
            else:
                form.instance.quantity += quantity
                self.object.delete()

        except SupplyItem.DoesNotExist:
            form.instance.supply_id = self.kwargs["supply_id"]
            self.object.delete()

        return super(SupplyUpdateSupplyItemUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ## parameters or data
        context["supply_id"] = self.kwargs["supply_id"]
        context["items"] = SupplyItem.objects.filter(
            supply_id=self.kwargs["supply_id"], is_original=False
        ).exclude(id=self.kwargs["pk"])

        supply = Supply.objects.get(id=self.kwargs["supply_id"])

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

        ## forms
        context["supply_form"] = SupplyMultiForm(
            instance={
                "supply": supply,
                "supplier": supply.supplier,
            }
        )
        context["item_form"] = context["form"]

        # for autocomplete
        product_json = list(
            Product.objects.values(
                "id",
                "designation",
                "unit_price",
                "marine_warehouses__quantity",
            )
        )
        context["products_data"] = product_json
        supplier_json = list(
            Supplier.objects.values(
                "company_name",
                "contact",
            )
        )
        context["suppliers_data"] = supplier_json

        return context

    def get_success_url(self):
        return reverse(
            "update_supply_list_supplyitem",
            args=[self.kwargs["supply_id"]],
        )


# delete


class SupplyUpdateSupplyItemDeleteView(LoginRequiredMixin, DeleteView):
    model = SupplyItem
    context_object_name = "supplyitem"
    template_name = "marine/supply/supply_update_supplyitem_confirm_delete.html"

    def get_success_url(self):
        return reverse(
            "update_supply_list_supplyitem",
            args=[self.kwargs["supply_id"]],
        )

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

        return context

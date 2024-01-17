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

# template variables
supply_create_template = "marine/supply/supply_create.html"


# This view simply redirects to the "create_supply_list_supplyitem" URL.
class InitiateSupplyCreateView(AdminStaffRequiredMixin, RedirectView):
    pattern_name = "create_supply_list_supplyitem"


# This view handles the validation of a supply and provides the necessary context data.
class ValidateSupplyCreateView(AdminStaffRequiredMixin, UpdateView):
    model = Supply
    form_class = SupplyMultiForm
    template_name = supply_create_template

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
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

        # Get the search keyword from the request GET parameters
        keyword = self.request.GET.get("search")

        # Filter the supply items based on the supply ID and is_original=True
        items = SupplyItem.objects.filter(
            supply_id=self.kwargs["pk"], is_original=True, is_temporary=False
        )

        # Apply additional filtering based on the keyword
        if keyword:
            items = items.filter(Q(product_designation__icontains=keyword))

        # Set the relevant data in the context
        context["supply_id"] = self.kwargs["pk"]
        context["items"] = items
        total_amount = items.aggregate(Sum("total_amount"))["total_amount__sum"]
        context["total_amount"] = total_amount if total_amount else 0

        # Set the forms in the context
        context["item_form"] = SupplyItemForm()
        context["supply_form"] = context["form"]

        # Retrieve the autocomplete data for products
        product_fields = [
            "id",
            "designation",
            "unit_price",
            "marine_warehouses__quantity",
        ]
        product_json = list(Product.objects.values(*product_fields))
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
        supply = self.get_object()
        supply.validate_bill
        return reverse("detail_supply", args=[supply.pk])


# This view handles the creation of a new supply by creating a Supply object and redirecting to InitiateSupplyCreateView or ValidateSupplyCreateView based on the request method.
class SupplyCreateView(AdminStaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if kwargs.get("pk") is None:
            supply = Supply.objects.create(added_by=self.request.user.employee)
            kwargs["supply_id"] = supply.id
        else:
            # transform "pk" to "supply_id"
            kwargs["supply_id"] = kwargs["pk"]
            del kwargs["pk"]
        view = InitiateSupplyCreateView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ValidateSupplyCreateView.as_view()
        return view(request, *args, **kwargs)


### SUPPLY ITEMS ###


# list
class SupplyCreateSupplyItemListView(AdminStaffRequiredMixin, ListView):
    model = SupplyItem
    template_name = supply_create_template
    context_object_name = "items"

    def get_queryset(self):
        # Retrieve the search keyword from the request GET parameters
        keyword = self.request.GET.get("search")

        # Filter the supply items based on the supply ID and is_original=True
        items = SupplyItem.objects.filter(
            supply_id=self.kwargs["supply_id"], is_original=True
        )

        # Apply additional filtering based on the keyword
        if keyword:
            items = items.filter(Q(product_designation__icontains=keyword))
        
        items = items.order_by("-id")

        return items


    def get_context_data(self):
        context = super().get_context_data()
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

        # Retrieve the supply items for the given supply ID, is_original=True and is_temporary=False
        supply_items = SupplyItem.objects.filter(
            supply_id=self.kwargs["supply_id"], is_original=True
        )

        # Calculate the total amount by summing the 'total_amount' field
        total_amount = supply_items.aggregate(Sum("total_amount"))["total_amount__sum"]
        context["total_amount"] = total_amount if total_amount else 0

        # Set the 'supply_id' in the context
        context["supply_id"] = self.kwargs["supply_id"]

        # Retrieve the supply object for the given supply ID
        supply = Supply.objects.get(id=self.kwargs["supply_id"])

        # Set the 'item_form' and 'supply_form' in the context
        context["item_form"] = SupplyItemForm()
        context["supply_form"] = SupplyMultiForm(
            instance={"supply": supply, "supplier": supply.supplier}
        )

        # Retrieve the autocomplete data for products
        product_fields = [
            "id",
            "designation",
            "unit_price",
            "marine_warehouses__quantity",
        ]
        product_json = list(Product.objects.values(*product_fields))
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
class SupplyCreateSupplyItemCreateView(AdminStaffRequiredMixin, CreateView):
    model = SupplyItem
    form_class = SupplyItemForm
    template_name = supply_create_template

    def form_valid(self, form):
        # Get the supply ID, product, and quantity from the form
        supply_id = self.kwargs.get("supply_id")
        product = form.cleaned_data.get("product")
        quantity = form.cleaned_data.get("quantity")

        try:
            quantity = form.instance.quantity
            form.instance = SupplyItem.objects.get(
                supply_id=self.kwargs["supply_id"],
                product=form.instance.product,
                is_original=True,
            )
            form.instance.quantity += quantity
            # supply_item.save()
        except SupplyItem.DoesNotExist:
            # If the supply item doesn't exist, set the supply ID and save the form
            form.instance.supply_id = supply_id
            # form.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the computer and shop based on the client's IP address
        computer = get_object_or_404(Computer, ip_address=get_client_ip(self.request))
        shop = computer.shop

        if self.request.user.is_staff:
            # If the user is a staff member, set alert, bill_alert, and salary_alert
            context["alert"] = warehouse_alert_function()
            context["bill_alert"] = bill_alert_function()
            context["salary_alert"] = salary_alert_function()
        else:
            # If the user is not a staff member, set alert and bill_alert based on the shop
            context["alert"] = store_alert_function(shop)
            context["bill_alert"] = bill_alert_function()

        # Set the supply_form and products_data in the context
        context["supply_form"] = SupplyMultiForm()

        # for autocomplete
        product_fields = [
            "id",
            "designation",
            "unit_price",
            "marine_warehouses__quantity",
        ]
        # Get product data as a JSON list with selected fields
        product_json = list(Product.objects.values(*product_fields))
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
        supply_id = self.kwargs["supply_id"]
        # Construct the success URL for listing supply items with the supply ID
        return reverse("create_supply_list_supplyitem", args=[supply_id])


# update
class SupplyCreateSupplyItemUpdateView(AdminStaffRequiredMixin, UpdateView):
    model = SupplyItem
    form_class = SupplyItemForm
    template_name = supply_create_template

    def form_valid(self, form):
        # Retrieve the quantity, supply ID, and product from the form's cleaned_data
        quantity = form.cleaned_data.get("quantity")
        supply_id = self.kwargs.get("supply_id")
        product = form.cleaned_data.get("product")

        try:
            # Check if a supply item with the given supply ID, product, and is_original=True exists
            supply_item = SupplyItem.objects.get(
                supply_id=supply_id,
                product=product,
                is_original=True,
            )

            if supply_item.pk == self.object.pk:
                # If the supply item is the same as the current object, update the price and quantity
                form.instance.price = self.object.price
                form.instance.quantity = quantity
            else:
                # If the supply item is different, increment its quantity and delete the current object
                supply_item.quantity += quantity
                supply_item.save()
                self.object.delete()
        except SupplyItem.DoesNotExist:
            # If the supply item doesn't exist, set the supply ID and save the form
            form.instance.supply_id = supply_id
            self.object.delete()
            form.save()

        return super().form_valid(form)

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

        supply_id = self.kwargs.get("supply_id")
        keyword = self.request.GET.get("search")

        items = SupplyItem.objects.filter(
            supply_id=supply_id,
            is_original=True,
        ).exclude(id=self.kwargs.get("pk"))

        if keyword:
            # Filter the items based on the keyword
            items = items.filter(Q(product_designation__icontains=keyword))

        supply = Supply.objects.get(id=supply_id)

        context["supply_id"] = supply_id
        context["items"] = items
        context["supply_form"] = SupplyMultiForm(
            instance={
                "supply": supply,
                "supplier": supply.supplier,
            }
        )
        context["item_form"] = context["form"]

        # for autocomplete
        product_fields = [
            "id",
            "designation",
            "unit_price",
            "marine_warehouses__quantity",
        ]
        # Retrieve the product data with selected fields as a JSON list
        product_json = list(Product.objects.values(*product_fields))
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
        supply_id = self.kwargs.get("supply_id")
        # Construct the success URL for listing supply items with the supply ID
        return reverse("create_supply_list_supplyitem", args=[supply_id])


# delete
class SupplyCreateSupplyItemDeleteView(AdminStaffRequiredMixin, DeleteView):
    model = SupplyItem
    context_object_name = "supplyitem"
    template_name = "marine/supply/supplyitem_confirm_delete.html"

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

    def get_success_url(self):
        supply_id = self.kwargs.get("supply_id")
        # Construct the success URL for listing supply items with the supply ID
        return reverse("create_supply_list_supplyitem", args=[supply_id])

from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.views.generic.base import RedirectView

from marine.loading.forms import LoadingForm, LoadingItemForm
from marine.loading.models import Loading, LoadingItem
from marine.methods import (
    bill_alert_function,
    get_client_ip,
    salary_alert_function,
    store_alert_function,
    warehouse_alert_function,
)
from marine.computer.models import Computer
from marine.product.models import Product
from marine.views import AdminStaffRequiredMixin

# variables
loading_create_template = "marine/loading/loading_create.html"


class InitiateLoadingCreateView(AdminStaffRequiredMixin, RedirectView):
    pattern_name = "create_loading_list_loadingitem"


class ValidateLoadingCreateView(AdminStaffRequiredMixin, UpdateView):
    model = Loading
    form_class = LoadingForm
    template_name = loading_create_template

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

        # parameters or data
        context["loading_id"] = self.kwargs["pk"]
        context["items"] = LoadingItem.objects.filter(
            loading_id=self.kwargs["pk"], is_original=True
        )
        context["total_amount"] = context["items"].aggregate(Sum("total_amount"))[
            "total_amount__sum"
        ]

        # form
        context["item_form"] = LoadingItemForm()
        context["loading_form"] = context["form"]

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

        return context

    def get_success_url(self):
        self.object.validate_bill
        return reverse("detail_loading", args=[self.kwargs["pk"]])


class LoadingCreateView(AdminStaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if kwargs.get("pk") is None:
            loading = Loading.objects.create(added_by=self.request.user.employee)
            kwargs["loading_id"] = loading.id
        else:
            # transform "pk" to "loading_id"
            kwargs["loading_id"] = kwargs["pk"]
            del kwargs["pk"]
        view = InitiateLoadingCreateView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ValidateLoadingCreateView.as_view()
        return view(request, *args, **kwargs)


### LOADING ITEMS ###


# list
class LoadingCreateLoadingItemListView(AdminStaffRequiredMixin, ListView):
    model = LoadingItem
    template_name = loading_create_template
    context_object_name = "items"

    def get_queryset(self):
        return LoadingItem.objects.filter(
            loading_id=self.kwargs["loading_id"], is_original=True
        ).order_by("-id")

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

        loading_items = LoadingItem.objects.filter(
            loading_id=self.kwargs["loading_id"], is_original=True
        )

        # parameters for the template
        if loading_items:
            context["total_amount"] = loading_items.aggregate(Sum("total_amount"))[
                "total_amount__sum"
            ]
        else:
            context["total_amount"] = 0
        context["loading_id"] = self.kwargs["loading_id"]

        loading = Loading.objects.get(id=self.kwargs["loading_id"])
        loading_queryset = Loading.objects.filter(bill_number=loading.bill_number)
        if len(loading_queryset) > 1:
            context["old_loading_id"] = loading_queryset[0].id

        # form to display
        context["item_form"] = LoadingItemForm()
        context["loading_form"] = LoadingForm(instance=loading)

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

        return context


# create
class LoadingCreateLoadingItemCreateView(AdminStaffRequiredMixin, CreateView):
    model = LoadingItem
    form_class = LoadingItemForm
    template_name = loading_create_template

    def form_valid(self, form):
        try:
            quantity = form.instance.quantity
            form.instance = LoadingItem.objects.get(
                loading_id=self.kwargs["loading_id"],
                product=form.instance.product,
                is_original=True,
            )
            form.instance.quantity += quantity
        except LoadingItem.DoesNotExist:
            form.instance.loading_id = self.kwargs["loading_id"]

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add the form instance with a custom name to the context
        context["item_form"] = context["form"]

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
        context["loading_form"] = LoadingForm()

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
        context["loading_id"] = self.kwargs["loading_id"]

        return context

    def get_success_url(self):
        return reverse(
            "create_loading_list_loadingitem", args=[self.kwargs["loading_id"]]
        )


# update
class LoadingCreateLoadingItemUpdateView(AdminStaffRequiredMixin, UpdateView):
    model = LoadingItem
    form_class = LoadingItemForm
    template_name = loading_create_template

    def form_valid(self, form):
        try:
            quantity = form.instance.quantity
            form.instance = LoadingItem.objects.get(
                loading_id=self.kwargs["loading_id"],
                product=form.instance.product,
                is_original=True,
            )
            if form.instance.pk == self.object.pk:
                form.instance.price = self.object.price
                form.instance.quantity = quantity
            else:
                form.instance.quantity += quantity
                self.object.delete()
        except LoadingItem.DoesNotExist:
            form.instance.loading_id = self.kwargs["loading_id"]
            self.object.delete()

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

        context["loading_id"] = self.kwargs["loading_id"]
        context["items"] = LoadingItem.objects.filter(
            loading_id=self.kwargs["loading_id"],
            is_original=True,
        ).exclude(id=self.kwargs["pk"])

        loading = Loading.objects.get(id=self.kwargs["loading_id"])
        loading_queryset = Loading.objects.filter(bill_number=loading.bill_number)
        if len(loading_queryset) > 1:
            context["old_loading_id"] = loading_queryset[0].id

        context["loading_form"] = LoadingForm(instance=loading)
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

        return context

    def get_success_url(self):
        return reverse(
            "create_loading_list_loadingitem", args=[self.kwargs["loading_id"]]
        )


# delete
class LoadingCreateLoadingItemDeleteView(AdminStaffRequiredMixin, DeleteView):
    model = LoadingItem
    context_object_name = "loadingitem"
    template_name = "marine/loading/loadingitem_confirm_delete.html"

    def get_success_url(self):
        return reverse(
            "create_loading_list_loadingitem", args=[self.kwargs["loading_id"]]
        )

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

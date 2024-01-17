from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
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
loading_update_template = "marine/loading/loading_update.html"


class InititateLoadingUpdateView(AdminStaffRequiredMixin, RedirectView):
    pattern_name = "update_loading_list_loadingitem"


class ValidateLoadingUpdateView(AdminStaffRequiredMixin, UpdateView):
    model = Loading
    form_class = LoadingForm
    template_name = loading_update_template

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
        items = LoadingItem.objects.filter(
            loading_id=self.kwargs["pk"], is_original=False
        )

        if keyword:
            items = items.filter(Q(product_designation__icontains=keyword))

        # parameters or data
        context["loading_id"] = self.kwargs["pk"]
        context["items"] = items
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
        loading = Loading.objects.get(id=self.kwargs["pk"])

        # delete original loadingitems
        for is_original_loadingitem in loading.item.filter(is_original=True):
            is_original_loadingitem.delete()

        # transform copied loadingitems to original
        for copied_loadingitem in loading.item.filter(is_original=False):
            copied_loadingitem.is_original = True
            copied_loadingitem.save()

        loading.validate_bill
        return reverse("detail_loading", args=[loading.id])


class LoadingUpdateView(AdminStaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # get the loading being updated
        loading = Loading.objects.get(id=self.kwargs["pk"])

        # check if there are already copied loadingitems
        exist_copied_loadingitems = loading.item.filter(is_original=False)

        # if they exist do nothing, if not set new ones
        if not exist_copied_loadingitems:
            # get a copy of original loadingitems
            copied_loadingitems = loading.item.filter(is_original=True)

            # reset the instances to new instances
            for copied_loadingitem in copied_loadingitems:
                copied_loadingitem.pk = None
                copied_loadingitem._state.adding = True
                copied_loadingitem.is_temporary = True  # to avoid altering the database
                copied_loadingitem.is_original = False  # set to copied
                copied_loadingitem.save()

            # link copied loadingitems to loading
            loading.item.set(copied_loadingitems)

        kwargs["loading_id"] = loading.id
        del kwargs["pk"]

        view = InititateLoadingUpdateView.as_view()

        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ValidateLoadingUpdateView.as_view()
        return view(request, *args, **kwargs)


class CancelLoadingUpdateView(LoginRequiredMixin, RedirectView):
    pattern_name = "detail_loading"

    def get_redirect_url(self, *args, **kwargs):
        loading = Loading.objects.get(id=self.kwargs["pk"])

        # delete copied loadingitems
        for is_original_loadingitem in loading.item.filter(is_original=False):
            is_original_loadingitem.delete()

        return super().get_redirect_url(*args, **kwargs)


### Loading Items ###


# list
class LoadingUpdateLoadingItemListView(LoginRequiredMixin, ListView):
    model = LoadingItem
    template_name = loading_update_template
    context_object_name = "items"

    def get_queryset(self):
        return LoadingItem.objects.filter(
            loading_id=self.kwargs["loading_id"], is_original=False
        ).order_by("-id")

    def get_context_data(self):
        context = super().get_context_data()

        loadingitems = LoadingItem.objects.filter(
            loading_id=self.kwargs["loading_id"], is_original=False
        )

        # parameters for the template
        if loadingitems:
            context["total_amount"] = loadingitems.aggregate(Sum("total_amount"))[
                "total_amount__sum"
            ]
        else:
            context["total_amount"] = 0
        context["loading_id"] = self.kwargs["loading_id"]

        loading = Loading.objects.get(id=self.kwargs["loading_id"])

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
class LoadingUpdateLoadingItemCreateView(LoginRequiredMixin, CreateView):
    model = LoadingItem
    form_class = LoadingItemForm
    template_name = loading_update_template

    def form_valid(self, form):
        try:
            quantity = form.instance.quantity
            form.instance = LoadingItem.objects.get(
                loading_id=self.kwargs["loading_id"],
                product=form.instance.product,
                is_original=False,
            )
            form.instance.quantity += quantity
        except LoadingItem.DoesNotExist:
            form.instance.loading_id = self.kwargs["loading_id"]

        form.instance.is_original = False

        return super(LoadingUpdateLoadingItemCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ## parameters or data
        context["loading_id"] = self.kwargs["loading_id"]

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
        context["loading_form"] = LoadingForm()
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
            "update_loading_list_loadingitem",
            args=[
                self.kwargs["loading_id"],
            ],
        )


# update
class LoadingUpdateLoadingItemUpdateView(LoginRequiredMixin, UpdateView):
    model = LoadingItem
    form_class = LoadingItemForm
    template_name = loading_update_template

    def form_valid(self, form):
        try:
            quantity = form.instance.quantity
            form.instance = LoadingItem.objects.get(
                loading_id=self.kwargs["loading_id"],
                product=form.instance.product,
                is_original=False,
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

        return super(LoadingUpdateLoadingItemUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ## parameters or data
        context["loading_id"] = self.kwargs["loading_id"]
        context["items"] = LoadingItem.objects.filter(
            loading_id=self.kwargs["loading_id"], is_original=False
        ).exclude(id=self.kwargs["pk"])

        loading = Loading.objects.get(id=self.kwargs["loading_id"])

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
            "update_loading_list_loadingitem",
            args=[
                self.kwargs["loading_id"],
            ],
        )


# delete
class LoadingUpdateLoadingItemDeleteView(LoginRequiredMixin, DeleteView):
    model = LoadingItem
    context_object_name = "loadingitem"
    template_name = "marine/loading/loading_update_loadingitem_confirm_delete.html"

    def get_success_url(self):
        return reverse(
            "update_loading_list_loadingitem",
            args=[
                self.kwargs["loading_id"],
            ],
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

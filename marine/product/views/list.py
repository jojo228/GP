from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q, Sum
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from marine.methods import (
    bill_alert_function,
    get_client_ip,
    salary_alert_function,
    store_alert_function,
    warehouse_alert_function,
)
from marine.computer.models import Computer
from marine.product.models import Product

product_list_template = "marine/product/product_list.html"


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = product_list_template
    paginate_by = 50

    def get_queryset(self):
        keyword = self.request.GET.get("search")

        object_list = Product.objects.annotate(
            warehouse_quantity=Sum("marine_warehouses__quantity"),
            warehouse_amount=Sum("marine_warehouses__quantity_amount"),
            bm1_quantity=Sum(
                "marine_stores__quantity",
                filter=Q(
                    marine_stores__shop__name__icontains="GP_Annexe_1",
                ),
            ),
            bm1_amount=Sum(
                "marine_stores__quantity_amount",
                filter=Q(
                    marine_stores__shop__name__icontains="GP_Annexe_1",
                ),
            ),
            bm2_quantity=Sum(
                "marine_stores__quantity",
                filter=Q(
                    marine_stores__shop__name__icontains="BM2",
                ),
            ),
            bm2_amount=Sum(
                "marine_stores__quantity_amount",
                filter=Q(
                    marine_stores__shop__name__icontains="BM2",
                ),
            ),
            bm3_quantity=Sum(
                "marine_stores__quantity",
                filter=Q(
                    marine_stores__shop__name__icontains="BM3",
                ),
            ),
            bm3_amount=Sum(
                "marine_stores__quantity_amount",
                filter=Q(
                    marine_stores__shop__name__icontains="BM3",
                ),
            ),
        ).order_by("designation")

        if keyword:
            object_list = object_list.filter(
                Q(designation__icontains=keyword)
            ).order_by("designation")
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


class ProductInWarehouseListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = product_list_template
    paginate_by = 50

    def get_queryset(self):
        keyword = self.request.GET.get("search")

        # get the actual and filter store and sold value
        computer = get_object_or_404(Computer, ip_address=get_client_ip(self.request))
        shop = computer.shop
        if self.request.user.is_staff:
            object_list = Product.objects.annotate(
                warehouse_quantity=Sum("marine_warehouses__quantity"),
                warehouse_amount=Sum("marine_warehouses__quantity_amount"),
                bm1_quantity=Sum(
                    "marine_stores__quantity",
                    filter=Q(
                        marine_stores__shop__name__icontains="GP_Annexe_1",
                    ),
                ),
                bm1_amount=Sum(
                    "marine_stores__quantity_amount",
                    filter=Q(
                        marine_stores__shop__name__icontains="GP_Annexe_1",
                    ),
                ),
                bm2_quantity=Sum(
                    "marine_stores__quantity",
                    filter=Q(
                        marine_stores__shop__name__icontains="BM2",
                    ),
                ),
                bm2_amount=Sum(
                    "marine_stores__quantity_amount",
                    filter=Q(
                        marine_stores__shop__name__icontains="BM2",
                    ),
                ),
                bm3_quantity=Sum(
                    "marine_stores__quantity",
                    filter=Q(
                        marine_stores__shop__name__icontains="BM3",
                    ),
                ),
                bm3_amount=Sum(
                    "marine_stores__quantity_amount",
                    filter=Q(
                        marine_stores__shop__name__icontains="BM3",
                    ),
                ),
            ).order_by("-warehouse_quantity", "designation")
        else:
            object_list = (
                Product.objects.filter(
                    marine_stores__shop=shop, marine_solds__shop=shop
                )
                .annotate(
                    store_quantity=Sum("marine_stores__quantity"),
                    sold_quantity=Sum("marine_solds__quantity"),
                )
                .order_by("-warehouse_quantity", "designation")
            )

        if keyword:
            object_list = object_list.filter(
                Q(designation__icontains=keyword)
            ).order_by("-warehouse_quantity", "designation")
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


class ProductListAlertView(LoginRequiredMixin, ListView):
    model = Product
    template_name = product_list_template

    def get_queryset(self):
        keyword = self.request.GET.get("search")

        # get the actual and filter store and sold value
        computer = get_object_or_404(Computer, ip_address=get_client_ip(self.request))
        shop = computer.shop
        if self.request.user.is_staff:
            object_list = (
                Product.objects.filter(
                    marine_warehouses__quantity__lt=F(
                        "marine_warehouses__quantity_alert"
                    ),
                )
                .annotate(
                    warehouse_quantity=Sum("marine_warehouses__quantity"),
                    warehouse_amount=Sum("marine_warehouses__quantity_amount"),
                    bm1_quantity=Sum(
                        "marine_stores__quantity",
                        filter=Q(
                            marine_stores__shop__name__icontains="GP_Annexe_1",
                        ),
                    ),
                    bm1_amount=Sum(
                        "marine_stores__quantity_amount",
                        filter=Q(
                            marine_stores__shop__name__icontains="GP_Annexe_1",
                        ),
                    ),
                    bm2_quantity=Sum(
                        "marine_stores__quantity",
                        filter=Q(
                            marine_stores__shop__name__icontains="BM2",
                        ),
                    ),
                    bm2_amount=Sum(
                        "marine_stores__quantity_amount",
                        filter=Q(
                            marine_stores__shop__name__icontains="BM2",
                        ),
                    ),
                    bm3_quantity=Sum(
                        "marine_stores__quantity",
                        filter=Q(
                            marine_stores__shop__name__icontains="BM3",
                        ),
                    ),
                    bm3_amount=Sum(
                        "marine_stores__quantity_amount",
                        filter=Q(
                            marine_stores__shop__name__icontains="BM3",
                        ),
                    ),
                )
                .order_by("designation")
            )
        else:
            object_list = (
                Product.objects.filter(
                    marine_stores__shop=shop,
                    marine_solds__shop=shop,
                    marine_stores__quantity__lt=F("marine_stores__quantity_alert"),
                )
                .annotate(
                    store_quantity=Sum("marine_stores__quantity"),
                    store_amount=Sum("marine_stores__quantity_amount"),
                    sold_quantity=Sum("marine_solds__quantity"),
                    sold_amount=Sum("marine_solds__quantity_amount"),
                )
                .order_by("designation")
            )

        if keyword:
            object_list = object_list.filter(
                Q(designation__icontains=keyword)
            ).order_by("designation")
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


class ProductListAlertPrintView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "marine/product/product_alert_print.html"

    def get_queryset(self):
        keyword = self.request.GET.get("search")

        # get the actual and filter store and sold value
        computer = get_object_or_404(Computer, ip_address=get_client_ip(self.request))
        shop = computer.shop
        if self.request.user.is_staff:
            object_list = (
                Product.objects.filter(
                    marine_warehouses__quantity__lt=F(
                        "marine_warehouses__quantity_alert"
                    ),
                )
                .annotate(
                    warehouse_quantity=Sum("marine_warehouses__quantity"),
                    warehouse_amount=Sum("marine_warehouses__quantity_amount"),
                    bm1_quantity=Sum(
                        "marine_stores__quantity",
                        filter=Q(
                            marine_stores__shop__name__icontains="GP_Annexe_1",
                        ),
                    ),
                    bm1_amount=Sum(
                        "marine_stores__quantity_amount",
                        filter=Q(
                            marine_stores__shop__name__icontains="GP_Annexe_1",
                        ),
                    ),
                    bm2_quantity=Sum(
                        "marine_stores__quantity",
                        filter=Q(
                            marine_stores__shop__name__icontains="BM2",
                        ),
                    ),
                    bm2_amount=Sum(
                        "marine_stores__quantity_amount",
                        filter=Q(
                            marine_stores__shop__name__icontains="BM2",
                        ),
                    ),
                    bm3_quantity=Sum(
                        "marine_stores__quantity",
                        filter=Q(
                            marine_stores__shop__name__icontains="BM3",
                        ),
                    ),
                    bm3_amount=Sum(
                        "marine_stores__quantity_amount",
                        filter=Q(
                            marine_stores__shop__name__icontains="BM3",
                        ),
                    ),
                )
                .order_by("designation")
            )
        else:
            object_list = (
                Product.objects.filter(
                    marine_stores__shop=shop,
                    marine_solds__shop=shop,
                    marine_stores__quantity__lt=F("marine_stores__quantity_alert"),
                )
                .annotate(
                    store_quantity=Sum("marine_stores__quantity"),
                    store_amount=Sum("marine_stores__quantity_amount"),
                    sold_quantity=Sum("marine_solds__quantity"),
                    sold_amount=Sum("marine_solds__quantity_amount"),
                )
                .order_by("designation")
            )

        if keyword:
            object_list = object_list.filter(
                Q(designation__icontains=keyword)
            ).order_by("designation")
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

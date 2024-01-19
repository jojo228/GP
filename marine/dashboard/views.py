import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import DataError
from django.db.models import Q, F, Sum, When, Case, Value, Count
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from marine.computer.models import Computer
from marine.methods import (
    bill_alert_function,
    get_client_ip,
    salary_alert_function,
    store_alert_function,
    warehouse_alert_function,
)
from marine.product.models import Product
from marine.sale.billing.model import Billing
from marine.shop.models import Shop



class DashboardView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "marine/dashboard/dashboard.html"

    def get_queryset(self):
        return (
            Product.objects.values("category")
            .annotate(
                solds_amount=Sum(
                    "marine_saleitems__total_amount",
                    filter=Q(
                        marine_saleitems__sale__date_modified__date=datetime.date.today()
                    )
                    & Q(marine_saleitems__is_temporary = 0)
                    & Q(marine_saleitems__sale__is_temporary = 0)
                    & (
                        Q(marine_saleitems__sale__category="OTR")
                        | Q(marine_saleitems__sale__category="CT")
                    ),
                ),
                solds_amount_credit=Sum(
                    "marine_saleitems__total_amount",
                    filter=Q(
                        marine_saleitems__sale__date_modified__date=datetime.date.today()
                    )
                    & Q(marine_saleitems__is_temporary = 0)
                    & Q(marine_saleitems__sale__is_temporary = 0)
                    & Q(marine_saleitems__sale__category="CR"),
                ),
                warehouses_amount=Sum("marine_saleitems__total_amount"),
            )
            .annotate(
                category_display=Case(
                    When(category="CB", then=Value("Câbles")),
                    When(category="FN", then=Value("Ventilateurs")),
                    When(category="PP", then=Value("Tuyaux")),
                    When(category="SL", then=Value("Ventes")),
                )
            )
        )
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        computer = get_object_or_404(Computer, ip_address=get_client_ip(self.request))
        actual_shop = computer.shop

        # Set the current shop in the context
        context["shop"] = actual_shop

        # Call the bill_alert_function() and store the result in the context
        context["bill_alert"] = bill_alert_function()

        # Set the "alert" based on the user's role
        context["alert"] = (
            warehouse_alert_function()  # If the user is staff, call warehouse_alert_function()
            if self.request.user.is_staff  # Otherwise, call store_alert_function() with the actual_shop
            else store_alert_function(actual_shop)
        )

        # Set the "salary_alert" based on the user's role
        context["salary_alert"] = (
            salary_alert_function()  # If the user is staff, call salary_alert_function()
            if self.request.user.is_staff  # Otherwise, set it to None
            else None
        )
        context["magasin"] = Product.objects.aggregate(
            # warehouse
            warehouse_amount=Sum("marine_warehouses__quantity_amount"),
            warehouse_items_quantity=Sum("marine_warehouses__quantity"),
            warehouse_quantity_percentage=(Sum("marine_warehouses__quantity") * 100)
            / Sum("marine_warehouses__quantity_initial"),
        )
        # Query and aggregate billing data for the current shop
        context["billing_" + "GP1"] = Billing.objects.aggregate(
            total_amount_paid=Sum(
                "amount_paid",
                filter=Q(
                    payment_date__date=datetime.date.today(),
                    sale__shop__name="GP1",
                ),
            ),
        )
        return context


class DashboardPrintView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "marine/dashboard/dashboard_print.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        computer = get_object_or_404(Computer, ip_address=get_client_ip(self.request))
        actual_shop = computer.shop
        context["shop"] = actual_shop
        context["current_date"] = datetime.date.today()
        if self.request.user.is_staff:
            context["alert"] = warehouse_alert_function()
            context["bill_alert"] = bill_alert_function()
            context["salary_alert"] = salary_alert_function()
        else:
            context["alert"] = store_alert_function(actual_shop)
            context["bill_alert"] = bill_alert_function()
        context["billing"] = Billing.objects.aggregate(
            total_amount_paid=Sum(
                "amount_paid",
                filter=Q(
                    payment_date__date=datetime.date.today(),
                    sale__shop=actual_shop,
                ),
            ),
        )
        context["magasin"] = Product.objects.aggregate(
            # warehouse
            warehouse_amount=Sum("marine_warehouses__quantity_amount"),
            warehouse_items_quantity=Sum("marine_warehouses__quantity"),
            warehouse_quantity_percentage=(Sum("marine_warehouses__quantity") * 100)
            / Sum("marine_warehouses__quantity_initial"),
        )

        # for summary of different shops
        if self.request.user.is_staff:
            shops = Shop.objects.all()
            for shop in shops:
                # define an empty dictionary for dashboard products summary
                # using items in store and items sold like key
                context[shop.name] = {"store": "", "sold": ""}

                # store aggregation
                context[shop.name]["store"] = Product.objects.filter(
                    marine_stores__shop__name=shop.name
                ).aggregate(
                    amount=Sum(
                        "marine_stores__quantity_amount",
                        filter=Q(
                            marine_stores__shop__name=shop.name,
                        ),
                    ),
                    items_quantity=Sum(
                        "marine_stores__quantity",
                        filter=Q(
                            marine_stores__shop__name=shop.name,
                        ),
                    ),
                    quantity_percentage=(Sum("marine_stores__quantity") * 100)
                    / (Sum("marine_stores__quantity_initial")),
                )

                # sold aggregation
                context[shop.name]["sold"] = Product.objects.filter(
                    marine_stores__shop__name=shop.name
                ).aggregate(
                    amount=Sum(
                        "marine_saleitems__total_amount",
                        filter=Q(
                            marine_saleitems__sale__date_modified__date=datetime.date.today(),
                            marine_saleitems__sale__shop__name=shop.name,
                        )
                        & (
                        Q(marine_saleitems__sale__category="OTR")
                        | Q(marine_saleitems__sale__category="CT")
                    ),
                    ),
                    amount_credit=Sum(
                        "marine_saleitems__total_amount",
                        filter=Q(
                            marine_saleitems__sale__date_modified__date=datetime.date.today(),
                            marine_saleitems__sale__shop__name=shop.name,
                        )
                        & Q(marine_saleitems__sale__category="CR"),
                    ),
                    items_quantity=Sum(
                        "marine_saleitems__quantity",
                        filter=Q(
                            marine_saleitems__sale__date_modified__date=datetime.date.today(),
                            marine_saleitems__sale__shop__name=shop.name,
                        ),
                    ),
                )

                # defining a context object for
                # retrieving bills of debt cleared
                key = "billing_" + shop.name
                context[key] = Billing.objects.aggregate(
                    total_amount_paid=Sum(
                        "amount_paid",
                        filter=Q(
                            payment_date__date=datetime.date.today(),
                            sale__shop__name=shop.name,
                        ),
                    ),
                )
        else:
            computer = get_object_or_404(
                Computer, ip_address=get_client_ip(self.request)
            )
            shop = computer.shop
            # define an empty dictionary for dashboard products summary
            # using items in store and items sold like key
            context["product"] = {"store": "", "sold": ""}

            # store aggregation
            context["product"]["store"] = Product.objects.filter(
                marine_stores__shop__name=shop.name
            ).aggregate(
                amount=Sum(
                    "marine_stores__quantity_amount",
                    filter=Q(
                        marine_stores__shop__name=shop.name,
                    ),
                ),
                items_quantity=Sum(
                    "marine_stores__quantity",
                    filter=Q(
                        marine_stores__shop__name=shop.name,
                    ),
                ),
                quantity_percentage=(Sum("marine_stores__quantity") * 100)
                / (Sum("marine_stores__quantity_initial")),
            )

            # sold aggregation
            context["product"]["sold"] = Product.objects.filter(
                marine_stores__shop__name=shop.name
            ).aggregate(
                amount=Sum(
                    "marine_saleitems__total_amount",
                    filter=Q(
                        marine_saleitems__sale__date_modified__date=datetime.date.today(),
                        marine_saleitems__sale__shop__name=shop.name,
                    )
                    & Q(marine_saleitems__sale__category="CT"),
                ),
                amount_credit=Sum(
                    "marine_saleitems__total_amount",
                    filter=Q(
                        marine_saleitems__sale__date_modified__date=datetime.date.today(),
                        marine_saleitems__sale__shop__name=shop.name,
                    )
                    & Q(marine_saleitems__sale__category="CR"),
                ),
                items_quantity=Sum(
                    "marine_saleitems__quantity",
                    filter=Q(
                        marine_saleitems__sale__date_modified__date=datetime.date.today(),
                        marine_saleitems__sale__shop__name=shop.name,
                    ),
                ),
            )

            # defining a context object for
            # retrieving bills of debt cleared
            key = "billing_" + shop.name
            context[key] = Billing.objects.aggregate(
                total_amount_paid=Sum(
                    "amount_paid",
                    filter=Q(
                        payment_date__date=datetime.date.today(),
                        sale__shop__name=shop.name,
                    ),
                ),
            )
        return context

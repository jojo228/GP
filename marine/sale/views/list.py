from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404
from django.views.generic import (
    ListView,
)
from marine.computer.models import Computer

from marine.methods import (
    bill_alert_function,
    get_client_ip,
    salary_alert_function,
    store_alert_function,
    warehouse_alert_function,
)
from marine.sale.filters import SaleFilter
from marine.sale.models import Sale


class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = "marine/sale/sale_list.html"
    paginate_by = 50

    def get_queryset(self):
        # Retrieve the keyword typed through the search bar
        keyword = self.request.GET.get("search")

        # Dictionary to map the category search
        category_keyword = {
            "PRO_FORMAT": "PF",
            "OTR": "OTR",
            "COMPTANT": "CT",
            "CREDIT": "CR",
        }

        # Retrieve the actual shop using its MAC address
        # and filter the sales' list
        computer = get_object_or_404(Computer, ip_address=get_client_ip(self.request))
        shop = computer.shop

        # Create a base queryset with filtering conditions
        base_queryset = Sale.objects.filter(
            Q(is_temporary=False) | (Q(is_temporary=True) & Q(added_by=self.request.user.employee))
        )
        # Apply additional filtering based on user, shop, and category conditions
        if not self.request.user.is_staff:
            base_queryset = base_queryset.filter(Q(shop=shop) | Q(category="PF"))

        # Apply keyword search filters if a keyword is provided
        if keyword:
            category = category_keyword.get(keyword.upper(), keyword)
            base_queryset = base_queryset.filter(
                Q(bill_number__contains=keyword) |
                Q(customer__name__icontains=keyword) |
                Q(category__icontains=category) |
                Q(customer__contact__contains=keyword) |
                Q(shop__name__icontains=keyword) |
                Q(date_created__icontains=keyword)
            )

        # Apply ordering based on the date_created field
        object_list = base_queryset.order_by("-date_created")

        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        computer = get_object_or_404(Computer, ip_address=get_client_ip(self.request))
        shop = computer.shop
        if self.request.user.is_staff:
            context["alert"] = warehouse_alert_function()
            context["bill_alert"] = bill_alert_function()
            context["salary_alert"] = salary_alert_function()

        else:
            context["alert"] = store_alert_function(shop)
            context["bill_alert"] = bill_alert_function()

        return context


class SaleListPrintView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = "marine/sale/sale_list_print.html"

    def get_queryset(self):
        # retrieve the keyword typed through search bar
        keyword = self.request.GET.get("search")

        # dictionnary to map the category search
        category_keyword = {
            "PRO_FORMAT": "PF",
            "COMPTANT": "CT",
            "CREDIT": "CR",
        }

        # retrieve the actual shop using it mac address
        # and filter the sales' list
        computer = get_object_or_404(Computer, ip_address=get_client_ip(self.request))
        shop = computer.shop
        if self.request.user.is_staff:
            object_list = Sale.objects.all().order_by("-date_created")
            ok = SaleFilter(
                self.request.GET, queryset=Sale.objects.all().order_by("-date_created")
            )
            object_list = ok.qs
        else:
            object_list = Sale.objects.all().filter(
                Q(shop=shop) | Q(category="PF"),
            )

        # if a keyword is typed, return sale corresponding to keyword
        if keyword:
            try:
                category = category_keyword[keyword.upper()]
            except KeyError:
                category = keyword
            object_list = object_list.filter(
                Q(bill_number__contains=keyword)
                | Q(customer__name__icontains=keyword)
                | Q(category__icontains=category)
                | Q(customer__contact__contains=keyword)
                | Q(shop__name__icontains=keyword)
                | Q(date_created__icontains=keyword)
            )
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        computer = get_object_or_404(Computer, ip_address=get_client_ip(self.request))
        shop = computer.shop
        if self.request.user.is_staff:
            context["alert"] = warehouse_alert_function()
            context["bill_alert"] = bill_alert_function()
            context["salary_alert"] = salary_alert_function()
            # define the filter form
            context["sale_date_filter"] = SaleFilter(
                self.request.GET, queryset=Sale.objects.all().order_by("-date_created")
            )
            context["date_filter_queryset"] = context["sale_date_filter"].qs

            if context["date_filter_queryset"]:
                context["total"] = context["date_filter_queryset"].aggregate(
                    Sum("total_amount")
                )["total_amount__sum"]
        else:
            context["alert"] = store_alert_function(shop)
            context["bill_alert"] = bill_alert_function()
        return context

from django.urls import include, path

from marine.sale.views.create import (
    SaleCreateView,
    SaleItemCreateView,
    SaleItemDeleteView,
    SaleItemListView,
    SaleItemUpdateView,
)
from marine.sale.views.delete import SaleDeleteView
from marine.sale.views.detail import DeliveryPrintView, SaleDetailView, SalePrintView
from marine.sale.views.list import SaleListPrintView, SaleListView
from marine.sale.views.update import (
    CancelSaleUpdateView,
    SaleUpdateView,
    UpdateSaleSaleItemCreateView,
    UpdateSaleSaleItemDeleteView,
    UpdateSaleSaleItemListView,
    UpdateSaleSaleItemUpdateView,
)

urlpatterns = [
    # sales
    path("", SaleListView.as_view(), name="list_sale"),
    path("create", SaleCreateView.as_view(), name="create_sale"),
    path("create/<int:pk>", SaleCreateView.as_view(), name="create_sale"),
    path("delete/<int:pk>", SaleDeleteView.as_view(), name="delete_sale"),
    path("delivery/<int:pk>",DeliveryPrintView.as_view(),name="print_delivery",),
    path("detail/<int:pk>", SaleDetailView.as_view(), name="detail_sale"),
    path("list/print",SaleListPrintView.as_view(),name="list_sale_print",),
    path("print/<int:pk>", SalePrintView.as_view(), name="print_sale"),
    path("update/<int:pk>", SaleUpdateView.as_view(), name="update_sale"),
    path("update/<int:pk>/cancel", CancelSaleUpdateView.as_view(), name="update_sale_cancel"),
    # sale items
    path("<int:sale_id>/item/create",SaleItemCreateView.as_view(),name="create_sale_create_saleitem",),
    path("<int:sale_id>/item/delete/<int:pk>",SaleItemDeleteView.as_view(),name="create_sale_delete_saleitem",),
    path("<int:sale_id>/item/update/<int:pk>",SaleItemUpdateView.as_view(),name="create_sale_update_saleitem",),
    path("<int:sale_id>/items",SaleItemListView.as_view(),name="create_sale_list_saleitem",),
    # update sale items
    path("update/<int:sale_id>/item/create",UpdateSaleSaleItemCreateView.as_view(),name="update_sale_create_saleitem",),
    path("update/<int:sale_id>/item/delete/<int:pk>",UpdateSaleSaleItemDeleteView.as_view(),name="update_sale_delete_saleitem",),
    path("update/<int:sale_id>/item/update/<int:pk>",UpdateSaleSaleItemUpdateView.as_view(),name="update_sale_update_saleitem",),
    path("update/<int:sale_id>/items",UpdateSaleSaleItemListView.as_view(),name="update_sale_list_saleitem",),
    # debtbilling
    path("<int:sale_id>/", include("marine.sale.billing.urls")),
]

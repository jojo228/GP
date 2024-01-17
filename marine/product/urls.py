from django.urls import path

from marine.product.views.create import ProductCreateView
from marine.product.views.delete import ProductDeleteView
from marine.product.views.detail import ProductDetailView
from marine.product.views.list import (
    ProductInWarehouseListView,
    ProductListAlertPrintView,
    ProductListAlertView,
    ProductListView,
)
from marine.product.views.update import ProductUpdateView

urlpatterns = [
    path("", ProductListView.as_view(), name="list_product"),
    path("alert", ProductListAlertView.as_view(), name="alert_list_product"),
    path(
        "alert/print",
        ProductListAlertPrintView.as_view(),
        name="alert_list_product_print",
    ),
    path(
        "warehouse", ProductInWarehouseListView.as_view(), name="product_in_warehouse"
    ),
    path("create", ProductCreateView.as_view(), name="create_product"),
    path("detail/<int:pk>", ProductDetailView.as_view(), name="detail_product"),
    path("update/<int:pk>", ProductUpdateView.as_view(), name="update_product"),
    path("delete/<int:pk>", ProductDeleteView.as_view(), name="delete_product"),
]

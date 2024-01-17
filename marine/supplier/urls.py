from django.urls import path

from marine.supplier.views.create import SupplierCreateView
from marine.supplier.views.delete import SupplierDeleteView
from marine.supplier.views.detail import SupplierDetailView
from marine.supplier.views.list import SupplierListView
from marine.supplier.views.update import SupplierUpdateView

urlpatterns = [
    path("supplier", SupplierListView.as_view(), name="list_supplier"),
    path("supplier/create", SupplierCreateView.as_view(), name="create_supplier"),
    path(
        "supplier/detail/<int:pk>",
        SupplierDetailView.as_view(),
        name="detail_supplier",
    ),
    path(
        "supplier/update/<int:pk>",
        SupplierUpdateView.as_view(),
        name="update_supplier",
    ),
    path(
        "supplier/delete/<int:pk>",
        SupplierDeleteView.as_view(),
        name="delete_supplier",
    ),
]

from django.urls import path

from marine.customer.views.create import CustomerCreateView
from marine.customer.views.delete import CustomerDeleteView
from marine.customer.views.detail import CustomerDetailView
from marine.customer.views.list import CustomerListView
from marine.customer.views.update import CustomerUpdateView

urlpatterns = [
    path("", CustomerListView.as_view(), name="list_customer"),
    path("create", CustomerCreateView.as_view(), name="create_customer"),
    path(
        "detail/<int:pk>",
        CustomerDetailView.as_view(),
        name="detail_customer",
    ),
    path(
        "update/<int:pk>",
        CustomerUpdateView.as_view(),
        name="update_customer",
    ),
    path(
        "delete/<int:pk>",
        CustomerDeleteView.as_view(),
        name="delete_customer",
    ),
]

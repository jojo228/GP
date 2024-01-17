from django.urls import path

from marine.sale.billing.views.create import BillingCreateView
from marine.sale.billing.views.delete import BillingDeleteView
from marine.sale.billing.views.detail import BillingDetailView, BillingPrintView
from marine.sale.billing.views.list import BillingAlertListView, BillingListView
from marine.sale.billing.views.update import BillingUpdateView

urlpatterns = [
    path("billing/create",BillingCreateView.as_view(),name="create_billing",),
    path("billing/delete/<int:pk>",BillingDeleteView.as_view(),name="delete_billing",),
    path("billing/detail/<int:pk>",BillingDetailView.as_view(),name="detail_billing",),
    path("billing/print/<int:pk>", BillingPrintView.as_view(), name="print_billing"),
    path("billing/update/<int:pk>",BillingUpdateView.as_view(),name="update_billing",),
    path("billings", BillingListView.as_view(), name="list_billing"),
    path("billings/alert", BillingAlertListView.as_view(), name="alert-list_billing"),
]

from django.urls import path

from marine.dashboard.views import DashboardPrintView, DashboardView


urlpatterns = [
    # dashboard
    path("", DashboardView.as_view(), name="dashboard"),
    path("print", DashboardPrintView.as_view(), name="dashboard_print"),
]

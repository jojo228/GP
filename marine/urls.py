from django.contrib.auth import views as auth_views
from django.urls import include, path

from marine.forms import AuthenticationFormWithContact

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="marine/login.html",
            authentication_form=AuthenticationFormWithContact,
        ),
        name="login",
    ),
    path("", include("marine.dashboard.urls")),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("computer/", include("marine.computer.urls")),
    path("customer/", include("marine.customer.urls")),
    path("employee/", include("marine.employee.urls")),
    path("inventory/", include("marine.inventory.urls")),
    path("loading/", include("marine.loading.urls")),
    path("product/", include("marine.product.urls")),
    path("sale/", include("marine.sale.urls")),
    path("shop/", include("marine.shop.urls")),
    path("supplier/", include("marine.supplier.urls")),
    path("supply/", include("marine.supply.urls")),
]

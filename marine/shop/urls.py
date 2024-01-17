from django.urls import path

from marine.shop.views.create import ShopCreateView
from marine.shop.views.delete import ShopDeleteView
from marine.shop.views.detail import ShopDetailView
from marine.shop.views.list import ShopListView
from marine.shop.views.update import ShopUpdateView

urlpatterns = [
    path("shop", ShopListView.as_view(), name="list_shop"),
    path("shop/create", ShopCreateView.as_view(), name="create_shop"),
    path(
        "shop/detail/<int:pk>",
        ShopDetailView.as_view(),
        name="detail_shop",
    ),
    path(
        "shop/update/<int:pk>",
        ShopUpdateView.as_view(),
        name="update_shop",
    ),
    path(
        "shop/delete/<int:pk>",
        ShopDeleteView.as_view(),
        name="delete_shop",
    ),
]

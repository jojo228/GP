from django.urls import path

from marine.supply.views.create import (
    SupplyCreateSupplyItemCreateView,
    SupplyCreateSupplyItemDeleteView,
    SupplyCreateSupplyItemListView,
    SupplyCreateSupplyItemUpdateView,
    SupplyCreateView,
)
from marine.supply.views.delete import SupplyDeleteView
from marine.supply.views.detail import SupplyDetailView
from marine.supply.views.list import SupplyListView
from marine.supply.views.update import (
    CancelSupplyUpdateView,
    SupplyUpdateView,
    SupplyUpdateSupplyItemCreateView,
    SupplyUpdateSupplyItemDeleteView,
    SupplyUpdateSupplyItemListView,
    SupplyUpdateSupplyItemUpdateView,
)

urlpatterns = [
    # supplys
    path("", SupplyListView.as_view(), name="list_supply"),
    path("create", SupplyCreateView.as_view(), name="create_supply"),
    path("create/<int:pk>", SupplyCreateView.as_view(), name="create_supply"),
    path("delete/<int:pk>", SupplyDeleteView.as_view(), name="delete_supply"),
    path("detail/<int:pk>", SupplyDetailView.as_view(), name="detail_supply"),
    path("update/<int:pk>", SupplyUpdateView.as_view(), name="update_supply"),
    path("update/<int:pk>/cancel", CancelSupplyUpdateView.as_view(), name="update_supply_cancel"),
    # create supply supplyitems
    path("create/<int:supply_id>/item/create",SupplyCreateSupplyItemCreateView.as_view(),name="create_supply_create_supplyitem",),
    path("create/<int:supply_id>/item/delete/<int:pk>",SupplyCreateSupplyItemDeleteView.as_view(),name="create_supply_delete_supplyitem",),
    path("create/<int:supply_id>/item/update/<int:pk>",SupplyCreateSupplyItemUpdateView.as_view(),name="create_supply_update_supplyitem",),
    path("create/<int:supply_id>/items",SupplyCreateSupplyItemListView.as_view(),name="create_supply_list_supplyitem",),
    # update supply supplyitems
    path("update/<int:supply_id>/item/create",SupplyUpdateSupplyItemCreateView.as_view(),name="update_supply_create_supplyitem",),
    path("update/<int:supply_id>/item/delete/<int:pk>",SupplyUpdateSupplyItemDeleteView.as_view(),name="update_supply_delete_supplyitem",),
    path("update/<int:supply_id>/item/update/<int:pk>",SupplyUpdateSupplyItemUpdateView.as_view(),name="update_supply_update_supplyitem",),
    path("update/<int:supply_id>/items",SupplyUpdateSupplyItemListView.as_view(),name="update_supply_list_supplyitem",),
]

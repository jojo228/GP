from django.urls import path

from marine.loading.views.create import (
    LoadingCreateLoadingItemCreateView,
    LoadingCreateLoadingItemDeleteView,
    LoadingCreateLoadingItemListView,
    LoadingCreateLoadingItemUpdateView,
    LoadingCreateView,
)
from marine.loading.views.delete import LoadingDeleteView
from marine.loading.views.detail import LoadingDetailView
from marine.loading.views.list import LoadingListView
from marine.loading.views.update import (
    CancelLoadingUpdateView,
    LoadingUpdateLoadingItemCreateView,
    LoadingUpdateLoadingItemDeleteView,
    LoadingUpdateLoadingItemListView,
    LoadingUpdateLoadingItemUpdateView,
    LoadingUpdateView,
)

urlpatterns = [
    # loadings
    path("", LoadingListView.as_view(), name="list_loading"),
    path("create", LoadingCreateView.as_view(), name="create_loading"),
    path("create/<int:pk>", LoadingCreateView.as_view(), name="create_loading"),
    path("delete/<int:pk>", LoadingDeleteView.as_view(), name="delete_loading"),
    path("detail/<int:pk>", LoadingDetailView.as_view(), name="detail_loading"),
    path("update/<int:pk>", LoadingUpdateView.as_view(), name="update_loading"),
    path("update/<int:pk>/cancel", CancelLoadingUpdateView.as_view(), name="update_loading_cancel"),
    # create loading loadingitems
    path("create/<int:loading_id>/item/create",LoadingCreateLoadingItemCreateView.as_view(),name="create_loading_create_loadingitem"),
    path("create/<int:loading_id>/item/delete/<int:pk>",LoadingCreateLoadingItemDeleteView.as_view(),name="create_loading_delete_loadingitem"),
    path("create/<int:loading_id>/item/update/<int:pk>",LoadingCreateLoadingItemUpdateView.as_view(),name="create_loading_update_loadingitem"),
    path("create/<int:loading_id>/items",LoadingCreateLoadingItemListView.as_view(),name="create_loading_list_loadingitem"),
    # update loading loadingitems
    path("update/<int:loading_id>/item/create",LoadingUpdateLoadingItemCreateView.as_view(),name="update_loading_create_loadingitem"),
    path("update/<int:loading_id>/item/delete/<int:pk>",LoadingUpdateLoadingItemDeleteView.as_view(),name="update_loading_delete_loadingitem"),
    path("update/<int:loading_id>/item/update/<int:pk>",LoadingUpdateLoadingItemUpdateView.as_view(),name="update_loading_update_loadingitem"),
    path("update/<int:loading_id>/items",LoadingUpdateLoadingItemListView.as_view(),name="update_loading_list_loadingitem"),
]

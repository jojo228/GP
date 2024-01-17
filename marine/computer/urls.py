from django.urls import path

from marine.computer.views.create import ComputerCreateView
from marine.computer.views.delete import ComputerDeleteView
from marine.computer.views.detail import ComputerDetailView
from marine.computer.views.list import ComputerListView
from marine.computer.views.update import ComputerUpdateView

urlpatterns = [
    path("", ComputerListView.as_view(), name="list_computer"),
    path("create", ComputerCreateView.as_view(), name="create_computer"),
    path("delete/<int:pk>",ComputerDeleteView.as_view(),name="delete_computer"),
    path("detail/<int:pk>",ComputerDetailView.as_view(),name="detail_computer"),
    path("update/<int:pk>",ComputerUpdateView.as_view(),name="update_computer"),
]

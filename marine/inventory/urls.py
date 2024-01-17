from django.urls import path

from marine.inventory.views import export_data, inventory

urlpatterns = [
    # inventory
    path("import", inventory, name="inventory"),
    # export_data
    path("export", export_data, name="export_data"),
]

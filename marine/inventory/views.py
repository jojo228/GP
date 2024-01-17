from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render

from marine.computer.models import Computer
from marine.methods import get_client_ip, product_loading, store_alert_function
from marine.sale.resources import (
    SaleItemRessource,
    SaleRessource,
    SupplyRessource,
    WarehouseRessource,
)

# variables
inventory_template = "marine/inventory.html"
export_content_type = "application/vnd.ms-excel"


def inventory(request):
    computer = get_object_or_404(Computer, ip_address=get_client_ip(request))
    shop = computer.shop
    alert = store_alert_function(shop)
    context = {
        "computer": computer,
        "shop": shop,
        "alert": alert,
    }
    if request.method == "POST":
        msga = product_loading(request.FILES["file"])
        context["msga"] = msga

    return render(request, inventory_template, context)


def export_data(request):
    computer = get_object_or_404(Computer, ip_address=get_client_ip(request))
    shop = computer.shop
    alert = store_alert_function(shop)
    if request.method == "POST":
        # Get selected option from form
        data = request.POST["data"]
        export_mapping = {
            "Sale": ("inventaire_vente.xlsx", SaleRessource),
            "SaleItem": ("produit_vendus.xlsx", SaleItemRessource),
            "Product": ("inventaire_achat.xlsx", SupplyRessource),
            "Warehouse": ("inventaire_stock.xlsx", WarehouseRessource),
        }
        if data in export_mapping:
            filename, resource_class = export_mapping[data]
            employee_resource = resource_class()
            dataset = employee_resource.export()
            response = HttpResponse(dataset.xlsx, content_type=export_content_type)
            response["Content-Disposition"] = 'attachment; filename="{}"'.format(
                filename
            )
            return response
    context = {
        "computer": computer,
        "shop": shop,
        "alert": alert,
    }
    return render(request, inventory_template, context)

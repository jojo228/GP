from django.contrib.auth.models import User
from import_export import fields, resources

from marine.employee.models import Employee
from marine.product.models import Warehouse
from marine.sale.models import Sale, SaleItem
from marine.supplier.models import Supplier
from marine.supply.models import Supply

facture_string = "N˚ FACTURE"


class SaleRessource(resources.ModelResource):
    def __init__(self, **kwargs):
        self.is_temporary = False

    def get_queryset(self):
        return Sale.objects.filter(is_temporary=self.is_temporary)

    bill_number = fields.Field(column_name=facture_string, attribute="bill_number")
    customer__name = fields.Field(
        column_name="CLIENT",
        attribute="customer__name",
    )
    net_amount = fields.Field(
        column_name="MONTANT NET",
        attribute="net_amount",
    )
    category = fields.Field(
        column_name="CATEGORIE",
        attribute="category",
    )
    items_number = fields.Field(
        column_name="NBRE D'ARTICLE",
        attribute="items_number",
    )
    date_created = fields.Field(
        column_name="CREER LE",
        attribute="date_created",
    )
    date_modified = fields.Field(
        column_name="MODIFIE LE",
        attribute="date_modified",
    )
    added_by__user__first_name = fields.Field(
        column_name="FAIT PAR",
        attribute="added_by__user__first_name",
    )
    shop__name = fields.Field(
        column_name="BOUTIQUE",
        attribute="shop__name",
    )

    class Meta:
        model = Sale
        fields = (
            "bill_number",
            "customer__name",
            "net_amount",
            "category",
            "items_number",
            "date_created",
            "date_modified",
            "added_by__user__first_name",
            "shop__name",
        )


class SaleItemRessource(resources.ModelResource):
    def __init__(self, **kwargs):
        self.is_temporary = False

    def get_queryset(self):
        return SaleItem.objects.filter(is_temporary=self.is_temporary)

    sale__bill_number = fields.Field(
        column_name=facture_string,
        attribute="sale__bill_number",
    )
    product__designation = fields.Field(
        column_name="DESIGNATION",
        attribute="product__designation",
    )
    quantity = fields.Field(
        column_name="QTE VENDU",
        attribute="quantity",
    )
    price = fields.Field(
        column_name="PRIX",
        attribute="price",
    )
    total_amount = fields.Field(
        column_name="MONTANT TOTAL",
        attribute="total_amount",
    )
    discount_price = fields.Field(
        column_name="REMISE",
        attribute="discount_price",
    )
    net_amount = fields.Field(
        column_name="MONTANT NET",
        attribute="net_amount",
    )

    class Meta:
        model = SaleItem
        fields = (
            "discount_price",
            "net_amount",
            "product__designation",
            "price",
            "total_amount",
            "quantity",
            "sale__bill_number",
        )


class EmployeeRessource(resources.ModelResource):
    class Meta:
        model = Employee


class UserRessource(resources.ModelResource):
    class Meta:
        model = User


class SupplyRessource(resources.ModelResource):
    def __init__(self, **kwargs):
        self.is_temporary = False

    def get_queryset(self):
        return Supplier.objects.filter(is_temporary=self.is_temporary)

    bill_number = fields.Field(
        column_name=facture_string,
        attribute="bill_number",
    )
    items_number = fields.Field(
        column_name="QTE ACHETE",
        attribute="items_number",
    )
    total_amount = fields.Field(
        column_name="MONTANT TOTAL",
        attribute="total_amount",
    )
    supplier__company_name = fields.Field(
        column_name="FOURNISSEUR",
        attribute="supplier__company_name",
    )
    date_created = fields.Field(
        column_name="DATE",
        attribute="date_created",
    )

    class Meta:
        model = Supply
        fields = (
            "bill_number",
            "supplier__company_name",
            "items_number",
            "date_created",
        )


class WarehouseRessource(resources.ModelResource):
    product__designation = fields.Field(
        column_name="DESIGNATION",
        attribute="product__designation",
    )
    product__unit_price = fields.Field(
        column_name="PRIX_UNITAIRE",
        attribute="product__unit_price",
    )
    quantity = fields.Field(
        column_name="QTES_EN_MAGAZIN",
        attribute="quantity",
    )
    quantity_alert = fields.Field(
        column_name="STOCK_MIN",
        attribute="quantity_alert",
    )

    class Meta:
        model = Warehouse
        fields = (
            "product__designation",
            "product__unit_price",
            "quantity",
            "quantity_alert",
        )

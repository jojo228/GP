from betterforms.multiform import MultiModelForm
from django import forms

from marine.product.models import Product, Warehouse
from marine.shop.models import Store


# This a form for adding a product
class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "input-bx"

    class Meta:
        model = Product
        fields = [
            "designation",
            "unit_price",
        ]
        labels = {
            "designation": "Désignation",
            "unit_price": "Prix unitaire",
        }


# This a form for adding alert quantity of a product in store
class StoreForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StoreForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "input-bx"

    class Meta:
        model = Store
        labels = {
            "quantity_alert": "Quantité d'alerte en boutique",
            "quantity": "Quantité en boutique",
        }
        fields = [
            "quantity_alert",
            "quantity",
        ]


# This a form for adding alert quantity of a product in warehouse
class WarehouseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WarehouseForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "input-bx"

    class Meta:
        model = Warehouse
        fields = [
            "quantity_alert",
            "quantity",
        ]
        labels = {
            "quantity_alert": "Quantité d'alerte en magasin",
            "quantity": "Quantité en magasin",
        }


class ProductMultiForm(MultiModelForm):
    form_classes = {
        "product": ProductForm,
        "store": StoreForm,
        "warehouse": WarehouseForm,
    }

    def save(self, commit=True):
        objects = super(ProductMultiForm, self).save(commit=False)

        if commit:
            # retrieve the product from the product form
            product = objects["product"]
            product.save()
            # get or create a sold instance
            warehouse = objects["warehouse"]
            warehouse.product = product
            warehouse.save()

        return objects

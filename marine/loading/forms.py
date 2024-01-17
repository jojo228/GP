from django import forms
from django.db.models import Sum

from marine.loading.models import Loading, LoadingItem
from marine.product.models import Warehouse

from rich import print


# This a form for adding a Loading bill's item
class LoadingItemForm(forms.ModelForm):
    class Meta:
        model = LoadingItem
        fields = [
            "product",
            "quantity",
            "price",
        ]
        labels = {
            "product": "Produit",
            "quantity": "Quantité",
            "price": "Prix",
        }
        widgets = {"product": forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-field"

    def clean(self):
        # Retrieve the cleaned form data
        cleaned_data = super().clean()
        print(f"the cleaned data is [green]{cleaned_data}[/green]")

        # Get the value of the "quantity" and "product" field
        quantity = cleaned_data.get("quantity")
        product = cleaned_data.get("product")

        # Check if the quantity is either 0 or None
        if quantity in {0, None}:
            # Raise a validation error if the quantity is invalid
            raise forms.ValidationError(
                "Le produit n'est pas disponible dans le magasin"
            )

        # Calculate the total quantity of temporary loading items, from other loading
        temporary_total_quantity = (
            LoadingItem.objects.filter(
                product_id=product,
                is_temporary=True,
                is_original=True,
            ).aggregate(total_quantity=Sum("quantity", default=0))
        )["total_quantity"]

        # Retrieve the warehouse object for the given product and shop
        warehouse = Warehouse.objects.filter(product_id=product).first()
        print(f"The product itself is [yellow]{product}[/yellow]")

        print(f"warehouse is [red]{warehouse}[/red]")

        # in case of update
        original_quantity = self.instance.quantity
        if original_quantity is not None and warehouse is not None:
            warehouse_quantity = original_quantity + warehouse.quantity
        elif warehouse:
            warehouse_quantity = warehouse.quantity

        # Check if the warehouse doesn't exist or the available quantity is less than the required quantity
        if warehouse is None:
            # Raise a validation error if the quantity is not available
            raise forms.ValidationError("Produit non disponible")

        if warehouse_quantity - (quantity + temporary_total_quantity) < 0:
            # Raise a validation error if the quantity is not available
            raise forms.ValidationError("Quantité non disponible")

        # Return the cleaned data
        return cleaned_data


class LoadingForm(forms.ModelForm):
    class Meta:
        model = Loading
        fields = [
            "supervised_by",
            "shop",
        ]
        labels = {
            "supervised_by": "Supervisé Par",
            "shop": "Boutique",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "input-bx"

    def clean(self):
        cleaned_data = super().clean()
        loading = self.instance
        if not loading.item.exists():
            raise forms.ValidationError("Empty Bill")
        return cleaned_data

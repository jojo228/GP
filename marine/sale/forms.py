from betterforms.multiform import MultiModelForm
from django import forms
from django.forms import RadioSelect

from marine.customer.models import Customer
from marine.sale.models import Sale, SaleItem


# SaleItemForm: Form for individual sale items
class SaleItemForm(forms.ModelForm):
    """Form for individual sale items."""

    class Meta:
        model = SaleItem
        fields = ["product", "quantity", "price", "discount_price", "total_amount"]
        labels = {
            "product": "Produit",
            "quantity": "Quantité",
            "price": "Prix",
            "discount_price": "Prix remise",
            "total_amount": "Montant Total",
        }
        widgets = {"product": forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-field"

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get("quantity")
        if quantity in {0, None}:
            raise forms.ValidationError(
                "Le produit n'est pas disponible dans la boutique"
            )
        return cleaned_data


# SaleForm: Form for the sale itself
class SaleForm(forms.ModelForm):
    """Form for the sale itself."""

    class Meta:
        model = Sale
        fields = [
            "total_amount",
            "date_created",
            "category",
        ]
        widgets = {
            "category": RadioSelect(),
        }
        labels = {
            "date_created": "Date",
            "category": "Catégorie",
            "total_amount": "Montant Total",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "input-bx"

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        original_category = self.instance.category if self.instance.pk else None

        # Check if the original category is "PF" and the changed category is either "CT" or "CR"
        if original_category != category:
            self.instance.is_temporary = True

        if not self.instance.item.exists():
            raise forms.ValidationError("Empty Bill")

        return cleaned_data


# SaleCustomerForm: Form for the customer information
class SaleCustomerForm(forms.ModelForm):
    """Form for the customer information."""

    class Meta:
        model = Customer
        fields = [
            "name",
            "contact",
        ]
        labels = {
            "name": "Nom du client",
            "contact": "Contact",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "input-bx"


# SaleMultiForm: Multi-model form combining multiple forms
class SaleMultiForm(MultiModelForm):
    """Multi-model form combining multiple forms."""

    form_classes = {
        "customer": SaleCustomerForm,
        "sale": SaleForm,
    }

    def save(self, commit=True):
        objects = super().save(commit=False)

        if commit:
            sale = objects["sale"]
            customer, _ = Customer.objects.get_or_create(
                name=objects["customer"].name, contact=objects["customer"].contact
            )
            sale.customer = customer
            customer.save()
            sale.save()

        return objects

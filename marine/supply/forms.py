from betterforms.multiform import MultiModelForm
from django import forms

from marine.supplier.models import Supplier
from marine.supply.models import Supply, SupplyItem


# This a form for adding a supply bill's item
class SupplyItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-field"

    class Meta:
        model = SupplyItem
        fields = [
            "product",
            "price",
            "quantity",
        ]
        labels = {
            "product": "Produit",
            "price": "Prix",
            "quantity": "Quantité",
        }
        widgets = {
            "product": forms.HiddenInput(),
        }


# This a form for filling a supply bill
class SupplyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["supervised_by"].widget.attrs["class"] = "input-bx"

    class Meta:
        model = Supply
        fields = [
            "supervised_by",
        ]
        labels = {
            "supervised_by": "Supervisé Par",
        }

    def clean(self):
        cleaned_data = super().clean()
        supply = self.instance
        if not supply.item.exists():
            raise forms.ValidationError("Empty Bill")
        return cleaned_data


# This is form for adding a new Supplier or retrieving while filling Supply bill


class SupplySupplierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SupplySupplierForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "input-bx"

    class Meta:
        model = Supplier
        fields = [
            "company_name",
            "contact",
        ]
        labels = {
            "company_name": "Nom de la societé",
            "contact": "Contact",
        }

    def clean(self):
        return self.cleaned_data


class SupplyMultiForm(MultiModelForm):
    form_classes = {
        "supply": SupplyForm,
        "supplier": SupplySupplierForm,
    }

    def save(self, commit=True):
        objects = super().save(commit=False)

        if commit:
            supply = objects["supply"]
            supplier, _ = Supplier.objects.update_or_create(
                contact=objects["supplier"].contact,
                defaults={"company_name": objects["supplier"].company_name},
            )
            supply.supplier = supplier
            supplier.save()
            supply.save()

        return objects

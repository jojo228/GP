from django import forms

from marine.supplier.models import Supplier


class SupplierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SupplierForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "input-bx"

    class Meta:
        model = Supplier
        fields = "__all__"
        labels = {
            "company_name": "Nom de la société",
            "manager_name": "Nom du manager",
            "address": "Adresse",
            "contact": "Contact",
        }

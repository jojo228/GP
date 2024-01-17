from django import forms

from marine.customer.models import Customer


# Here we define all the forms required to be displayed in the template for users' input
# The forms will be defined in the following sequence
# Product | Supply | Loading | Sale | Employee | Supplier | Customer

# repetitive string
empty_bill = "Empty Bill"
prix_remise = "Prix remise"
quantity = "Quantité"


# This is form for adding a new Customer
class CustomerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "input-bx"

    class Meta:
        model = Customer
        fields = "__all__"
        labels = {
            "name": "Nom du client",
            "address": "Adresse",
            "contact": "Contact",
        }

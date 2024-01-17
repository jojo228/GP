from django import forms

from marine.sale.billing.model import Billing


class BillingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BillingForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "input-bx"

    class Meta:
        model = Billing
        fields = [
            "amount_paid",
            "next_payment_date",
        ]
        labels = {
            "amount_paid": "Montant payé",
            "next_payment_date": "Date du prochain paiment",
        }

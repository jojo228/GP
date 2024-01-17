from django import forms

from marine.computer.models import Computer


class ComputerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ComputerForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "input-bx"
            if visible.errors:
                visible.field.widget.attrs["class"] = " input-bx_error"

    class Meta:
        model = Computer
        fields = "__all__"
        labels = {
            "name": "Fonction de l'ordinateur",
            "shop": "Boutique de l'ordinateur",
            "ip_address": "Addresse Ip de l'ordinateur",
        }

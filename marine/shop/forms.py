from django import forms

from marine.product.models import Product
from marine.shop.models import Shop, Sold, Store


class ShopForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ShopForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "input-bx"

    class Meta:
        model = Shop
        fields = [
            "name",
        ]
        labels = {
            "name": "Nom de la boutique",
        }

    def save(self, commit=True):
        shop = super(ShopForm, self).save()

        if commit:
            # loop the products
            for product in Product.objects.all():
                # get or create a store instance
                Store.objects.get_or_create(product=product, shop=shop)
                # get or create a sold instance
                Sold.objects.get_or_create(product=product, shop=shop)

        return shop

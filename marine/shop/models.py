from django.db import models
from django.urls import reverse

from marine.product.models import Product, ProductQuantityInfo

related_name_string = "%(app_label)s_%(class)s_related"
related_query_name_string = "%(app_label)s_%(class)ss"


class Shop(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )
    stores = models.ManyToManyField(
        Product,
        through="Store",
        related_name="store_related",
        related_query_name="stores",
    )
    solds = models.ManyToManyField(Product, through="Sold")

    def get_absolute_url(self):
        return reverse("detail_shop", kwargs={"pk": self.pk})

    @property
    def get_update_url(self):
        return reverse("update_shop", kwargs={"pk": self.pk})

    @property
    def get_delete_url(self):
        return reverse("delete_shop", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name


# store information
class Store(ProductQuantityInfo):
    quantity_alert = models.IntegerField(default=0)
    quantity_initial = models.IntegerField(default=0)
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name=related_name_string,
        related_query_name=related_query_name_string,
    )

    # sold information


class Sold(ProductQuantityInfo):
    quantity_amount_credit = models.IntegerField(default=0)
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name=related_name_string,
        related_query_name=related_query_name_string,
    )

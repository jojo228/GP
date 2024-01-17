from django.db import models
from django.urls import reverse


related_name_string = "%(app_label)s_%(class)s_related"
related_query_name_string = "%(app_label)s_%(class)ss"

# -------------------------- About Product -------------------------------#


class Product(models.Model):
    designation = models.CharField(max_length=200, unique=True)
    unit_price = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse("detail_product", kwargs={"pk": self.pk})

    def __str__(self):
        return self.designation

    @property
    def get_update_url(self):
        return reverse("update_product", kwargs={"pk": self.pk})

    @property
    def get_delete_url(self):
        return reverse("delete_product", kwargs={"pk": self.pk})


# --------------------- Abstract Class -------------------------------------#


# this an abstract model that contains information that are shared between
# quantity of product in warehouse, store and sold
class ProductQuantityInfo(models.Model):
    quantity = models.IntegerField(default=0)
    quantity_amount = models.IntegerField(default=0)
    quantity_date_added = models.DateTimeField(auto_now_add=True)
    quantity_date_modified = models.DateTimeField(auto_now=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name=related_name_string,
        related_query_name=related_query_name_string,
    )

    # update or assign the price to product
    def save(self, *args, **kwargs):
        self.quantity_amount = self.product.unit_price * self.quantity
        super(ProductQuantityInfo, self).save(*args, **kwargs)

    class Meta:
        abstract = True


# warehouse information
class Warehouse(ProductQuantityInfo):
    quantity_alert = models.IntegerField(default=0)
    quantity_initial = models.IntegerField(default=0)
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name=related_name_string,
        related_query_name=related_query_name_string,
    )

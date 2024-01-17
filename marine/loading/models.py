from django.db import models
from django.db.models import F
from django.urls import reverse

from marine.employee.models import Employee
from marine.models import BillCommonInfo, ProductCommonInfo
from marine.product.models import Warehouse
from marine.shop.models import Shop, Store


class Loading(BillCommonInfo):
    """Loading model represents a loading transaction and inherits from BillCommonInfo model."""

    bill_identifier = "CHARG"
    supervised_by = models.ForeignKey(
        Employee, on_delete=models.PROTECT, blank=True, null=True
    )
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT, blank=True, null=True)


class LoadingItem(ProductCommonInfo):
    """LoadingItem model represents an item in a loading transaction and inherits from ProductCommonInfo model."""

    loading = models.ForeignKey(Loading, on_delete=models.PROTECT, related_name="item")

    def save(self, *args, **kwargs):
        """Save method overridden to update product quantities."""
        self.total_amount = self.price * self.quantity
        super().save(*args, **kwargs)  # Call superclass save method
        if not self.is_temporary and self.is_original and not self.loading.is_temporary:
            self._update_product_quantities()  # Update product quantities

    def delete(self, *args, **kwargs):
        """Delete method overridden to update product quantities."""
        if not self.is_temporary and self.is_original and not self.loading.is_temporary:
            self._update_product_quantities(
                delete=True
            )  # Update product quantities for deletion
        super().delete(*args, **kwargs)  # Call superclass delete method

    def _update_product_quantities(self, delete=False):
        """Update the product quantities in store and warehouse."""
        quantity_change = -self.quantity if delete else self.quantity
        amount_change = -self.total_amount if delete else self.total_amount

        # Update store quantities
        store_update = {
            "quantity": F("quantity") + quantity_change,
            "quantity_amount": F("quantity_amount") + amount_change,
            "quantity_initial": F("quantity") + quantity_change,
        }
        Store.objects.select_for_update().filter(
            product=self.product, shop=self.loading.shop
        ).update(**store_update)

        # Update warehouse quantities
        warehouse_update = {
            "quantity": F("quantity") - quantity_change,
            "quantity_amount": F("quantity_amount") - amount_change,
        }
        Warehouse.objects.select_for_update().filter(product=self.product).update(
            **warehouse_update
        )

    def get_absolute_url(self):
        """Get the absolute URL for the loading item."""
        return reverse(
            "create_loading_list_loadingitem",
            kwargs={"loading_id": self.loading.pk},
        )

    @property
    def get_create_loading_update_url(self):
        """Get the URL for updating the loading item in create mode."""
        return reverse(
            "create_loading_update_loadingitem",
            kwargs={"pk": self.pk, "loading_id": self.loading.pk},
        )

    @property
    def get_create_loading_delete_url(self):
        """Get the URL for deleting the loading item in create mode."""
        return reverse(
            "create_loading_delete_loadingitem",
            kwargs={"pk": self.pk, "loading_id": self.loading.pk},
        )

    @property
    def get_update_loading_absolute_url(self):
        """Get the absolute URL for the loading item in update mode."""
        return reverse(
            "update_loading_list_loadingitem",
            kwargs={"loading_id": self.loading.pk},
        )

    @property
    def get_update_loading_update_url(self):
        """Get the URL for updating the loading item in update mode."""
        return reverse(
            "update_loading_update_loadingitem",
            kwargs={"pk": self.pk, "loading_id": self.loading.pk},
        )

    @property
    def get_update_loading_delete_url(self):
        """Get the URL for deleting the loading item in update mode."""
        return reverse(
            "update_loading_delete_loadingitem",
            kwargs={"pk": self.pk, "loading_id": self.loading.pk},
        )

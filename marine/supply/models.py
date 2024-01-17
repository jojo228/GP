from django.db import models, transaction
from django.db.models import F
from django.urls import reverse

from marine.employee.models import Employee
from marine.models import BillCommonInfo, ProductCommonInfo
from marine.product.models import Warehouse
from marine.supplier.models import Supplier


class Supply(BillCommonInfo):
    bill_identifier = "ACHA"

    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, blank=True, null=True
    )
    supervised_by = models.ForeignKey(
        Employee, on_delete=models.PROTECT, blank=True, null=True
    )


class SupplyItem(ProductCommonInfo):
    supply = models.ForeignKey(Supply, on_delete=models.PROTECT, related_name="item")

    def save(self, *args, **kwargs):
        self.total_amount = self.price * self.quantity
        if (
            (not self.is_temporary)
            and (self.is_original)
            and (not self.supply.is_temporary)
        ):
            with transaction.atomic():
                self._update_product_quantity()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if (
            (not self.is_temporary)
            and (self.is_original)
            and (not self.supply.is_temporary)
        ):
            with transaction.atomic():
                self._update_product_quantity(deleted=True)
                
        super().delete(*args, **kwargs)

    def _update_product_quantity(self, deleted=False):
        quantity_change = -self.quantity if deleted else self.quantity
        amount_change = -self.total_amount if deleted else self.total_amount

        warehouse_update = {
            "quantity": F("quantity") + quantity_change,
            "quantity_amount": F("quantity_amount") + amount_change,
            "quantity_initial": F("quantity") + quantity_change,
        }

        Warehouse.objects.select_for_update().filter(product=self.product).update(
            **warehouse_update
        )

    def get_absolute_url(self):
        return reverse(
            "create_supply_list_supplyitem",
            kwargs={"supply_id": self.supply.pk},
        )

    @property
    def get_create_supply_update_url(self):
        return reverse(
            "create_supply_update_supplyitem",
            kwargs={"pk": self.pk, "supply_id": self.supply.pk},
        )

    @property
    def get_create_supply_delete_url(self):
        return reverse(
            "create_supply_delete_supplyitem",
            kwargs={"pk": self.pk, "supply_id": self.supply.pk},
        )

    @property
    def get_update_supply_absolute_url(self):
        return reverse(
            "update_supply_list_supplyitem",
            kwargs={"supply_id": self.supply.pk},
        )

    @property
    def get_update_supply_update_url(self):
        return reverse(
            "update_supply_update_supplyitem",
            kwargs={"pk": self.pk, "supply_id": self.supply.pk},
        )

    @property
    def get_update_supply_delete_url(self):
        return reverse(
            "update_supply_delete_supplyitem",
            kwargs={"pk": self.pk, "supply_id": self.supply.pk},
        )

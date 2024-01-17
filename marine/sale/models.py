from django.db import models, transaction
from django.db.models import F
from django.urls import reverse

from marine.customer.models import Customer
from marine.models import BillCommonInfo, ProductCommonInfo
from marine.shop.models import Shop, Sold, Store



class Sale(BillCommonInfo):
    """Sale model represents a sale transaction and inherits from BillCommonInfo model."""
    # Constants for bill categories
    PRO_FORMAT = "PF"
    COMPTANT = "CT"
    CREDIT = "CR"
    BILL_CATEGORY_CHOICES = [
        (COMPTANT, "Comptant"),
        (CREDIT, "Credit"),
        (PRO_FORMAT, "Proforma"),
    ]

    # Fields of the Sale model
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, blank=True, null=True
    )
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT, blank=True, null=True)
    amount_in_letters = models.CharField(max_length=150)
    category = models.CharField(
        max_length=3,
        choices=BILL_CATEGORY_CHOICES,
        default=COMPTANT,
    )

    @property
    def print_absolute_url(self):
        """Returns the absolute URL for printing the sale."""
        return reverse("print_sale", kwargs={"pk": self.pk})

    @property
    def billing_absolute_url(self):
        """Returns the absolute URL for listing the billing information of the sale."""
        return reverse("list_billing", kwargs={"sale_id": self.pk})



class SaleItem(ProductCommonInfo):
    """SaleItem model represents an item in a sale transaction and inherits from ProductCommonInfo model."""
    
    # Fields of the SaleItem model
    discount_price = models.IntegerField()
    net_amount = models.IntegerField()
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name="item")
    tax_amount = models.IntegerField(default=0)
    tax_rate = models.IntegerField(default=0)
    tax_type = models.CharField(max_length=10)

    def save(self, *args, **kwargs):
        """Overrides the save method to update related models and perform necessary calculations."""
        self.net_amount = self.price * self.quantity
        self.total_amount = self.discount_price * self.quantity
        self.tax_amount = (
            self.discount_price * (100 + self.tax_rate) / 100
        ) * self.quantity
        # Check conditions before updating related models
        if (
            (not self.is_temporary)
            and (self.is_original)
            and (not self.sale.is_temporary)
            and (self.sale.category != "PF")
        ):
            with transaction.atomic():
                self._update_store_sold()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Overrides the delete method to update related models."""
        # Check conditions before updating related models
        if (
            (not self.is_temporary)
            and (self.is_original)
            and (not self.sale.is_temporary)
            and (self.sale.category != "PF")
        ):
            with transaction.atomic():
                self._update_store_sold(delete=True)
        super().delete(*args, **kwargs)

    def _update_store_sold(self, delete=False):
        """Updates the Sold and Store models based on the sale item changes."""
        quantity_change = -self.quantity if delete else self.quantity
        amount_change = -self.total_amount if delete else self.total_amount

        # Update Sold data
        sold_update = {
            "quantity": F("quantity") + quantity_change,
            "quantity_amount": F("quantity_amount") + amount_change,
        }
        if self.sale.category == "CR":
            sold_update["quantity_amount_credit"] = (
                F("quantity_amount_credit") + amount_change
            )
        Sold.objects.filter(product=self.product, shop=self.sale.shop).update(
            **sold_update
        )

        # Update Store data
        store_update = {
            "quantity": F("quantity") - quantity_change,
            "quantity_amount": F("quantity_amount") - amount_change,
        }
        Store.objects.filter(product=self.product, shop=self.sale.shop).update(
            **store_update
        )

    def get_absolute_url(self):
        """Returns the absolute URL for creating a sale item."""
        return reverse(
            "create_sale_list_saleitem",
            kwargs={"sale_id": self.sale.pk},
        )

    @property
    def get_create_sale_update_url(self):
        """Returns the absolute URL for updating a sale item."""
        return reverse(
            "create_sale_update_saleitem",
            kwargs={"pk": self.pk, "sale_id": self.sale.pk},
        )

    @property
    def get_create_sale_delete_url(self):
        """Returns the absolute URL for deleting a sale item."""
        return reverse(
            "create_sale_delete_saleitem",
            kwargs={"pk": self.pk, "sale_id": self.sale.pk},
        )

    @property
    def get_update_sale_absolute_url(self):
        """Returns the absolute URL for updating the sale."""
        return reverse(
            "update_sale_list_saleitem",
            kwargs={"sale_id": self.sale.pk},
        )

    @property
    def get_update_sale_update_url(self):
        """Returns the absolute URL for updating a sale item within the sale update view."""
        return reverse(
            "update_sale_update_saleitem",
            kwargs={"pk": self.pk, "sale_id": self.sale.pk},
        )

    @property
    def get_update_sale_delete_url(self):
        """Returns the absolute URL for deleting a sale item within the sale update view."""
        return reverse(
            "update_sale_delete_saleitem",
            kwargs={"pk": self.pk, "sale_id": self.sale.pk},
        )

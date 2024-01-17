from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone
from num2words import num2words

from marine.employee.models import Employee
from marine.product.models import Product

related_name_string = "%(app_label)s_%(class)s_related"
related_query_name_string = "%(app_label)s_%(class)ss"


### Abstract Classes Definition


# this an abstract model that contains information that are shared between
# sale, loading and supply items
class ProductCommonInfo(models.Model):
    date_modified = models.DateTimeField(auto_now=True)
    is_original = models.BooleanField(default=True)
    is_temporary = models.BooleanField(default=True)
    price = models.IntegerField()
    quantity = models.PositiveIntegerField()
    total_amount = models.IntegerField()
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name=related_name_string,
        related_query_name=related_query_name_string,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.product.designation


# this an abstract model that contains information that are shared between
# sale, loading anf supply bill
class BillCommonInfo(models.Model):
    bill_identifier = None  # to use as bill identifier in the bill number
    bill_number = models.CharField(max_length=50)
    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(auto_now=True)
    is_temporary = models.BooleanField(default=True)
    items_number = models.IntegerField(default=0)
    total_amount = models.IntegerField(default=0)

    added_by = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name=related_name_string,
        related_query_name=related_query_name_string,
    )

    def save(self, *args, **kwargs):
        # if it is a temporary bill,
        # which means the bill has not been validated yet
        # and does not have any bill number yet
        if self.is_temporary and not self.bill_number:
            temporary_string = "TP-"

            # Get the last temporary bill's number
            last_bill_number = (
                self.__class__.objects.filter(
                    bill_number__startswith=temporary_string, is_temporary=True
                )
                .values_list("bill_number", flat=True)
                .last()
            )

            # Determine the actual bill number based on the last bill number
            actual_bill_number = (
                int(last_bill_number[3:]) + 1 if last_bill_number else 1
            )

            # Generate the actual temporay bill number
            self.bill_number = f"{temporary_string}{actual_bill_number:07d}"

        # Call the parent save method
        super().save(*args, **kwargs)

    @property
    def validate_bill(self):
        # if it is a temporary bill,
        # which means the bill has not been validated yet
        if self.is_temporary:
            if self.__class__.__name__ == "Sale":
                # create a dictionnary for category with the corresponding string
                category_string = {"PF": "PRO-", "CR": "FC-", "CT": "FCO-"}
                self.bill_identifier = category_string[self.category]

            # Get the last validated bill's number
            last_bill_number = (
                self.__class__.objects.filter(
                    bill_number__startswith=self.bill_identifier, is_temporary=False
                )
                .order_by("date_modified")
                .values_list("bill_number", flat=True)
                .last()
            )

            # Determine the actual bill number based on the last bill number
            actual_invoice_number = (
                int(last_bill_number[len(self.bill_identifier) :]) + 1
                if last_bill_number
                else 1
            )

            # Generate the actual bill number
            self.bill_number = f"{self.bill_identifier}{actual_invoice_number:07d}"

            self.is_temporary = (
                False  # to avoid generating a tempory bill number when it will be saved
            )

        # retrieve the original items
        items = self.item.filter(is_original=True)

        # loop over to apply the custom save, to alter the database
        for item in items:
            item.is_temporary = False  # to allow the actions on the database
            item.save()

        # Update the items count and total amount
        self.items_number = items.count()
        self.total_amount = items.aggregate(Sum("total_amount"))["total_amount__sum"]

        if self.__class__.__name__ == "Sale":
            self.amount_in_letters = num2words(self.total_amount, lang="fr")

        # Save the changes
        self.save()

    def delete(self, *args, **kwargs):
        # if the bill is not temporay
        # which means it has been validated
        if not self.is_temporary:
            # loop over the items to perform the custom delete
            for item in self.item.all():
                item.delete()
        else:
            self.item.all().delete()
        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            f"detail_{self.__class__.__name__.lower()}", kwargs={"pk": self.pk}
        )

    @property
    def get_update_url(self):
        return reverse(
            f"update_{self.__class__.__name__.lower()}", kwargs={"pk": self.pk}
        )

    @property
    def get_delete_url(self):
        return reverse(
            f"delete_{self.__class__.__name__.lower()}", kwargs={"pk": self.pk}
        )

    def __str__(self):
        return self.bill_number

    class Meta:
        abstract = True

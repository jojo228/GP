from django.db import models
from django.urls import reverse
from django.utils import timezone
from num2words import num2words

from marine.customer.models import Customer
from marine.employee.models import Employee
from marine.sale.models import Sale

related_name_string = "%(app_label)s_%(class)s_related"
related_query_name_string = "%(app_label)s_%(class)ss"


# a model representing the bill delivered when paying debt
class Billing(models.Model):
    bill_number = models.CharField(max_length=50)
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name="billings")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    added_by = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name=related_name_string,
        related_query_name=related_query_name_string,
    )
    amount_paid = models.IntegerField(default=0)
    amount_left = models.IntegerField(default=0)
    amount_in_letters = models.CharField(max_length=200)
    wording = models.CharField(max_length=200)
    next_payment_date = models.DateField()
    payment_date = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(auto_now=True)
    is_temporary = models.BooleanField(default=True)

    # update the product information by adding quantity after bill being validated
    def save(self, *args, **kwargs):
        billings = Billing.objects.filter(sale=self.sale)
        if self.is_temporary:
            if bool(billings):
                billing = billings.order_by("payment_date").reverse()[0]

                # in case of update, if there's only one bill, then the amount_left is the total_amount minus the amount_paid
                if (billing.bill_number == self.bill_number) and (len(billings) == 1):
                    self.amount_left = self.sale.total_amount - self.amount_paid
                else:
                    if (billing.bill_number == self.bill_number) and (
                        len(billings) >= 1
                    ):
                        billing = billings.order_by("payment_date").reverse()[1]
                    self.amount_left = billing.amount_left - self.amount_paid
            else:
                self.amount_left = self.sale.total_amount - self.amount_paid
        self.amount_in_letters = num2words(self.amount_paid, lang="fr")
        super().save(*args, **kwargs)

    # A property to be called when the Bill is being validated
    # It generates an Id number to each bill using the day's date plus three (3) digits
    @property
    def validate_bill(self):
        # check first if the debt bill has already a bill number
        # to avoid to change an existing bill number
        if not self.bill_number:
            # generate a bill number
            debtbilling_string = "S"
            next_invoice_number = "00001"
            last_invoice = (
                Billing.objects.filter(bill_number__startswith=debtbilling_string)
                .order_by("bill_number")
                .last()
            )
            if last_invoice:
                last_invoice_number = int(last_invoice.bill_number[1:])
                next_invoice_number = "{0:05d}".format(last_invoice_number + 1)
            self.bill_number = debtbilling_string + next_invoice_number
            # set temporary to false to avoid operation on amount
            # which we are not trying to do here
            self.is_temporary = False
            self.save()

        # Convert amount into words
        self.amount_in_letters = num2words(self.amount_paid, lang="fr")
        # set temporary to false to avoid operation on amount
        # which we are not trying to do here
        self.is_temporary = False
        self.save()

    def get_absolute_url(self):
        return reverse("detail_billing", kwargs={"pk": self.pk, "sale_id": self.sale.pk})

    @property
    def get_update_url(self):
        return reverse("update_billing", kwargs={"pk": self.pk, "sale_id": self.sale.pk})

    @property
    def get_delete_url(self):
        return reverse("delete_billing", kwargs={"pk": self.pk, "sale_id": self.sale.pk})

    @property
    def print_absolute_url(self):
        return reverse("print_billing", kwargs={"pk": self.pk, "sale_id": self.sale.pk})

    def __str__(self):
        return self.bill_number
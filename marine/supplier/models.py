from django.db import models
from django.urls import reverse


class Supplier(models.Model):
    company_name = models.CharField(max_length=50)
    manager_name = models.CharField(max_length=50, blank=True)
    contact = models.PositiveIntegerField(null=True, blank=True)
    address = models.CharField(max_length=150, blank=True)

    def get_absolute_url(self):
        return reverse("detail_supplier", kwargs={"pk": self.pk})

    @property
    def get_update_url(self):
        return reverse("update_supplier", kwargs={"pk": self.pk})

    @property
    def get_delete_url(self):
        return reverse("delete_supplier", kwargs={"pk": self.pk})

    def __str__(self):
        return self.company_name

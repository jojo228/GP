from django.db import models
from django.urls import reverse


# a model to store information about customers of the structure
class Customer(models.Model):
    name = models.CharField(max_length=50, blank=True)
    contact = models.PositiveIntegerField(null=True, blank=True)
    address = models.CharField(max_length=150, blank=True)

    def get_absolute_url(self):
        return reverse("detail_customer", kwargs={"pk": self.pk})

    @property
    def get_update_url(self):
        return reverse("update_customer", kwargs={"pk": self.pk})

    @property
    def get_delete_url(self):
        return reverse("delete_customer", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name

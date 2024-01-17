from django.urls import reverse
from django.db import models
from marine.shop.models import Shop


related_name_string = "%(app_label)s_%(class)s_related"
related_query_name_string = "%(app_label)s_%(class)ss"


class Computer(models.Model):
    name = models.CharField(
        max_length=100,
    )
    ip_address = models.GenericIPAddressField(
        unique=True,
    )
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name=related_name_string,
        related_query_name=related_query_name_string,
    )

    def get_absolute_url(self):
        return reverse("detail_computer", kwargs={"pk": self.pk})

    @property
    def get_update_url(self):
        return reverse("update_computer", kwargs={"pk": self.pk})

    @property
    def get_delete_url(self):
        return reverse("delete_computer", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name

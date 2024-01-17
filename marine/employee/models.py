from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


# a model to store information about employees of the structure
class Employee(models.Model):
    # setting the list of choices for sex

    MALE = "M"
    FEMALE = "F"
    SEX_CHOICES = [
        (MALE, "Masculin"),
        (FEMALE, "Féminin"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact = models.PositiveIntegerField(unique=True)
    sex = models.CharField(
        max_length=1,
        choices=SEX_CHOICES,
    )
    address = models.CharField(max_length=150, blank=True)
    salary = models.IntegerField(null=True, blank=True)
    salary_payment_date = models.DateField(null=True, blank=True)
    position = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.first_name

    def get_absolute_url(self):
        return reverse("detail_employee", kwargs={"pk": self.pk})

    @property
    def get_update_url(self):
        return reverse("update_employee", kwargs={"pk": self.pk})

    @property
    def get_delete_url(self):
        return reverse("delete_employee", kwargs={"pk": self.pk})

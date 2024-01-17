from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

from .models import Employee


class MyBackend(BaseBackend):
    def authenticate(self, request, **kwargs):
        try:
            contact = kwargs["contact"]
        except KeyError:
            return None
        password = kwargs["password"]
        try:
            user = Employee.objects.get(contact=contact).user
            if user.check_password(password) is True:
                return user

            return None
        except Employee.DoesNotExist:
            return None

    def get_user(self, contact):
        try:
            return Employee.objects.get(pk=contact).user
        except (User.DoesNotExist, Employee.DoesNotExist):
            return None

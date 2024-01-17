from betterforms.multiform import MultiModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from marine.employee.models import Employee


# --------------------------------- Employee ------------------------------------------------------#
class UserRegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "input-bx"

    class Meta:
        model = User
        fields = ["first_name", "last_name"]
        labels = {
            "first_name": "Nom",
            "last_name": "Prénoms",
            "password1": "Mot de Passe",
        }


# This is form for adding and creating account of a new employee


class EmployeeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "input-bx"

    class Meta:
        model = Employee
        exclude = [
            "user",
        ]
        labels = {
            "contact": "Contact",
            "sex": "Sexe",
            "address": "Adresse",
            "salary": "Salaire",
            "salary_payment_date": "Date de paiment de Salaire",
            "position": "Poste",
        }


class EmployeeMultiForm(MultiModelForm):
    form_classes = {
        "user": UserRegisterForm,
        "employee": EmployeeForm,
    }

    def save(self, commit=True):
        objects = super(EmployeeMultiForm, self).save(commit=False)

        if commit:
            user = objects["user"]
            employee = objects["employee"]
            user.username = employee.contact
            user.save()
            employee.user = user
            employee.save()

        return objects

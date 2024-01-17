from django.urls import path

from marine.employee.views.create import EmployeeCreateView
from marine.employee.views.delete import EmployeeDeleteView
from marine.employee.views.detail import EmployeeDetailView
from marine.employee.views.list import EmployeeAlertListView, EmployeeListView
from marine.employee.views.update import EmployeeUpdateView

urlpatterns = [
    # employees
    path("", EmployeeListView.as_view(), name="list_employee"),
    path("alert", EmployeeAlertListView.as_view(), name="employee_alert_list"),
    path("create", EmployeeCreateView.as_view(), name="create_employee"),
    path("detail/<int:pk>", EmployeeDetailView.as_view(), name="detail_employee"),
    path("update/<int:pk>", EmployeeUpdateView.as_view(), name="update_employee"),
    path("delete/<int:pk>", EmployeeDeleteView.as_view(), name="delete_employee"),
]
